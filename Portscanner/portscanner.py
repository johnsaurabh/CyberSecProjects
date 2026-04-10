from __future__ import annotations

import argparse
import json
import socket
import threading
from queue import Queue


def parse_ports(port_argument: str) -> list[int]:
    ports: set[int] = set()
    for chunk in port_argument.split(","):
        item = chunk.strip()
        if not item:
            continue
        if "-" in item:
            start_text, end_text = item.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise ValueError(f"Invalid port range: {item}")
            ports.update(range(start, end + 1))
        else:
            ports.add(int(item))

    invalid_ports = [port for port in ports if port < 1 or port > 65535]
    if invalid_ports:
        raise ValueError(f"Ports must be between 1 and 65535: {sorted(invalid_ports)}")
    return sorted(ports)


def scan_port(target: str, port: int, timeout: float) -> dict[str, object]:
    result = {
        "port": port,
        "open": False,
        "error": None,
    }
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            connection_result = sock.connect_ex((target, port))
            result["open"] = connection_result == 0
    except OSError as exc:
        result["error"] = str(exc)
    return result


def run_scanner(target: str, ports: list[int], timeout: float, max_threads: int) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    queue: Queue[int] = Queue()
    results_lock = threading.Lock()

    for port in ports:
        queue.put(port)

    def worker() -> None:
        while not queue.empty():
            try:
                port = queue.get_nowait()
            except Exception:
                return
            result = scan_port(target, port, timeout)
            with results_lock:
                results.append(result)
            queue.task_done()

    threads = []
    worker_count = min(max_threads, len(ports)) or 1
    for _ in range(worker_count):
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return sorted(results, key=lambda item: int(item["port"]))


def print_human_results(target: str, results: list[dict[str, object]]) -> None:
    print(f"Scanning {target}...")
    open_ports = [item for item in results if item["open"]]
    for item in open_ports:
        print(f"[+] Port {item['port']} is open")
    print(f"Completed scan. Open ports: {len(open_ports)} / {len(results)} checked.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Lightweight threaded TCP port scanner")
    parser.add_argument("--target", required=True, help="IPv4 address or hostname to scan")
    parser.add_argument("--ports", default="20-1024", help='Port list or ranges, e.g. "22,80,443,8000-8010"')
    parser.add_argument("--timeout", type=float, default=0.75, help="Per-port socket timeout in seconds")
    parser.add_argument("--threads", type=int, default=100, help="Maximum worker threads")
    parser.add_argument("--json", action="store_true", help="Print structured JSON results")
    args = parser.parse_args()

    ports = parse_ports(args.ports)
    results = run_scanner(args.target, ports, timeout=args.timeout, max_threads=args.threads)

    if args.json:
        print(json.dumps({"target": args.target, "results": results}, indent=2))
        return

    print_human_results(args.target, results)


if __name__ == "__main__":
    main()
