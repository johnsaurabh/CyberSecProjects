from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from scapy.all import DNS, DNSQR, DNSRR, IP, IPv6, UDP, rdpcap, sniff, wrpcap  # type: ignore


SUPPORTED_TYPES = {1: "A", 28: "AAAA"}


@dataclass
class DetectionFinding:
    query: str
    record_type: str
    observed_value: str
    expected_values: list[str]
    source_ip: str
    summary: str

    def to_row(self) -> dict[str, str]:
        return {
            "query": self.query,
            "record_type": self.record_type,
            "observed_value": self.observed_value,
            "expected_values": ", ".join(self.expected_values),
            "source_ip": self.source_ip,
            "summary": self.summary,
        }


def load_expected_records(path: Path) -> dict[str, dict[str, list[str]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    normalized: dict[str, dict[str, list[str]]] = {}
    for domain, records in payload.items():
        normalized[domain.lower().rstrip(".")] = {
            "A": [str(item) for item in records.get("A", [])],
            "AAAA": [str(item) for item in records.get("AAAA", [])],
        }
    return normalized


def iter_answers(answer: DNSRR | None, count: int) -> Iterable[DNSRR]:
    current = answer
    for _ in range(count):
        if current is None:
            break
        yield current
        current = current.payload if isinstance(current.payload, DNSRR) else None


def source_ip_for_packet(packet) -> str:
    if packet.haslayer(IP):
        return packet[IP].src
    if packet.haslayer(IPv6):
        return packet[IPv6].src
    return "unknown"


def detect_spoofing(packet, expected_records: dict[str, dict[str, list[str]]]) -> list[DetectionFinding]:
    findings: list[DetectionFinding] = []
    if not packet.haslayer(DNS):
        return findings

    dns_layer = packet[DNS]
    if dns_layer.qr != 1 or not packet.haslayer(DNSQR) or dns_layer.ancount == 0:
        return findings

    query = packet[DNSQR].qname.decode("utf-8", errors="ignore").rstrip(".").lower()
    expected = expected_records.get(query)
    if not expected:
        return findings

    for answer in iter_answers(dns_layer.an, dns_layer.ancount):
        record_type = SUPPORTED_TYPES.get(answer.type)
        if not record_type:
            continue
        observed_value = str(answer.rdata)
        expected_values = expected.get(record_type, [])
        if expected_values and observed_value not in expected_values:
            findings.append(
                DetectionFinding(
                    query=query,
                    record_type=record_type,
                    observed_value=observed_value,
                    expected_values=expected_values,
                    source_ip=source_ip_for_packet(packet),
                    summary=f"DNS answer mismatch for {query}: observed {observed_value}, expected one of {expected_values}",
                )
            )
    return findings


def write_findings_csv(findings: list[DetectionFinding], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["query", "record_type", "observed_value", "expected_values", "source_ip", "summary"],
        )
        writer.writeheader()
        for finding in findings:
            writer.writerow(finding.to_row())


def analyze_pcap(pcap_path: Path, expected_path: Path, output_path: Path | None = None) -> list[DetectionFinding]:
    expected_records = load_expected_records(expected_path)
    packets = rdpcap(str(pcap_path))
    findings: list[DetectionFinding] = []
    for packet in packets:
        findings.extend(detect_spoofing(packet, expected_records))
    if output_path:
        write_findings_csv(findings, output_path)
    return findings


def live_callback(expected_records: dict[str, dict[str, list[str]]], output_path: Path | None):
    findings: list[DetectionFinding] = []

    def _callback(packet) -> None:
        packet_findings = detect_spoofing(packet, expected_records)
        if not packet_findings:
            return
        findings.extend(packet_findings)
        for finding in packet_findings:
            print(f"[ALERT] {finding.summary}")
        if output_path:
            write_findings_csv(findings, output_path)

    return _callback


def generate_demo_pcap(output_path: Path, expected_path: Path) -> dict[str, object]:
    expected = load_expected_records(expected_path)
    packets = []

    def build_packet(domain: str, rdata: str, answer_type: int, src_ip: str):
        return IP(src=src_ip, dst="192.168.1.50") / UDP(sport=53, dport=53000) / DNS(
            id=0xAAAA,
            qr=1,
            qd=DNSQR(qname=domain),
            an=DNSRR(rrname=domain, type=answer_type, ttl=300, rdata=rdata),
            ancount=1,
        )

    legit_a = expected["example.com"]["A"][0]
    spoofed_a = "203.0.113.77"
    legit_aaaa = expected["ipv6.example.com"]["AAAA"][0]
    spoofed_aaaa = "2001:db8::bad"

    packets.append(build_packet("example.com", legit_a, 1, "8.8.8.8"))
    packets.append(build_packet("example.com", spoofed_a, 1, "203.0.113.10"))
    packets.append(build_packet("ipv6.example.com", legit_aaaa, 28, "8.8.4.4"))
    packets.append(build_packet("ipv6.example.com", spoofed_aaaa, 28, "198.51.100.10"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output_path), packets)
    return {
        "pcap_path": str(output_path),
        "packet_count": len(packets),
        "spoof_examples": [
            {"query": "example.com", "fake_a": spoofed_a},
            {"query": "ipv6.example.com", "fake_aaaa": spoofed_aaaa},
        ],
    }


def print_findings(findings: list[DetectionFinding]) -> None:
    if not findings:
        print("No spoofing mismatches detected.")
        return
    for finding in findings:
        print(
            json.dumps(
                {
                    "query": finding.query,
                    "record_type": finding.record_type,
                    "observed_value": finding.observed_value,
                    "expected_values": finding.expected_values,
                    "source_ip": finding.source_ip,
                }
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="DNS spoofing detector with offline PCAP analysis and optional live sniffing")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze-pcap", help="Analyze a PCAP file for spoofed DNS answers")
    analyze_parser.add_argument("--pcap", required=True, help="PCAP file to analyze")
    analyze_parser.add_argument("--expected", default="sample_expected_records.json", help="JSON file with expected DNS answers")
    analyze_parser.add_argument("--output", help="Optional CSV output path for findings")

    live_parser = subparsers.add_parser("live-sniff", help="Sniff live DNS traffic and alert on mismatches")
    live_parser.add_argument("--expected", default="sample_expected_records.json", help="JSON file with expected DNS answers")
    live_parser.add_argument("--output", help="Optional CSV output path for findings")
    live_parser.add_argument("--count", type=int, help="Optional packet count limit")

    demo_parser = subparsers.add_parser("generate-demo", help="Generate a sample PCAP containing legitimate and spoofed DNS answers")
    demo_parser.add_argument("--output", default="samples/sample_dns_spoof.pcap", help="Demo PCAP output path")
    demo_parser.add_argument("--expected", default="sample_expected_records.json", help="JSON file with expected DNS answers")

    args = parser.parse_args()

    if args.command == "analyze-pcap":
        findings = analyze_pcap(
            pcap_path=Path(args.pcap),
            expected_path=Path(args.expected),
            output_path=Path(args.output) if args.output else None,
        )
        print_findings(findings)
        print(json.dumps({"finding_count": len(findings)}))
        return

    if args.command == "live-sniff":
        expected_records = load_expected_records(Path(args.expected))
        callback = live_callback(expected_records, Path(args.output) if args.output else None)
        print("[INFO] Starting DNS spoof detector. Press Ctrl+C to stop.")
        sniff(filter="udp port 53", prn=callback, store=False, count=args.count)
        return

    if args.command == "generate-demo":
        print(json.dumps(generate_demo_pcap(Path(args.output), Path(args.expected)), indent=2))
        return


if __name__ == "__main__":
    main()
