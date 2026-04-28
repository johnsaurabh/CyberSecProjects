# DNSSpoof_Detector

## Overview

`DNSSpoof_Detector` is a DNS-answer validation tool designed to identify suspicious DNS responses by comparing observed `A` and `AAAA` records against an expected-record baseline. It supports:

- offline PCAP analysis for safe and reproducible validation
- optional live DNS sniffing for real-time monitoring
- CSV export of spoofing findings
- demo PCAP generation for local validation

The offline workflow can be executed and validated locally without requiring real attack traffic.

## Capabilities

- DNS packet parsing with Scapy
- detection of mismatched `A` and `AAAA` DNS answers
- offline network-forensics validation using PCAP files
- structured CSV logging of security findings
- defensive network monitoring workflow

## Tech Stack

- Python 3
- Scapy for packet parsing and PCAP handling
- Standard library: `argparse`, `csv`, `json`, `pathlib`

## Project Structure

```text
DNSSpoof_Detector/
|-- Spoof_detector.py
|-- README.md
|-- requirements.txt
|-- sample_expected_records.json
`-- samples/
```

After running the demo workflow, the `samples/` directory contains:

- `sample_dns_spoof.pcap`
- `findings.csv`

## Requirements

```powershell
python -m pip install -r requirements.txt
```

## Expected-Record Baseline

The detector compares observed DNS responses against a JSON file containing known-good answers. Example format:

```json
{
  "example.com": {
    "A": ["93.184.216.34"],
    "AAAA": []
  },
  "ipv6.example.com": {
    "A": [],
    "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"]
  }
}
```

## Usage

### 1. Generate a demo PCAP

```powershell
cd D:\Cybersec\DNSSpoof_Detector
python Spoof_detector.py generate-demo --output samples\sample_dns_spoof.pcap --expected sample_expected_records.json
```

This generates a PCAP containing:

- legitimate `A` and `AAAA` DNS answers
- spoofed `A` and `AAAA` DNS answers

### 2. Analyze the demo PCAP

```powershell
python Spoof_detector.py analyze-pcap --pcap samples\sample_dns_spoof.pcap --expected sample_expected_records.json --output samples\findings.csv
```

Expected behavior:

- spoofed answers are printed to the console
- findings are written to `samples\findings.csv`

## Sample Findings Artifact

Once generated, the sample findings file can be reviewed directly:

- `samples/findings.csv`

### 3. Live sniffing

```powershell
python Spoof_detector.py live-sniff --expected sample_expected_records.json --output samples\live_findings.csv
```

Notes:

- live sniffing requires packet-capture privileges
- this mode is best for a local lab or test VM

## Example Detection Output

```json
{"query": "example.com", "record_type": "A", "observed_value": "203.0.113.77", "expected_values": ["93.184.216.34"], "source_ip": "203.0.113.10"}
{"query": "ipv6.example.com", "record_type": "AAAA", "observed_value": "2001:db8::bad", "expected_values": ["2606:2800:220:1:248:1893:25c8:1946"], "source_ip": "2001:db8::10"}
{"finding_count": 2}
```

## Limitations

- detection quality depends on the correctness of the expected baseline file
- this project validates answer mismatches, not all possible DNS attack techniques
- live sniffing depends on local packet-capture privileges and environment support
- encrypted DNS protocols such as DoH and DoT are out of scope
- some Scapy environments on Windows may print a `libpcap` warning during offline processing, but offline PCAP generation and analysis still work
