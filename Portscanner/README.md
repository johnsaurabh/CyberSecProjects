# Portscanner

## Overview

`Portscanner` is a lightweight threaded TCP port scanner for local lab validation and basic network enumeration. It supports:

- configurable targets
- custom port lists and ranges
- timeout tuning
- structured JSON output
- reproducible local validation

This version keeps the original project simple while making it more usable, testable, and presentable in a public repository.

## What The Project Demonstrates

- TCP port reachability testing
- threaded network scanning
- CLI-based security utility design
- human-readable and machine-readable output modes

## Usage

### Basic scan

```powershell
cd D:\Cybersec\Portscanner
python portscanner.py --target 127.0.0.1 --ports 22,80,443
```

### Port range scan

```powershell
python portscanner.py --target 127.0.0.1 --ports 20-1024
```

### JSON output

```powershell
python portscanner.py --target 127.0.0.1 --ports 80,443,8080 --json
```

### Custom timeout and thread count

```powershell
python portscanner.py --target 127.0.0.1 --ports 1-1000 --timeout 0.5 --threads 50
```

## Example Output

```text
Scanning 127.0.0.1...
[+] Port 80 is open
[+] Port 443 is open
Completed scan. Open ports: 2 / 3 checked.
```

## Notes

- this scanner performs TCP connect scans only
- it does not perform service fingerprinting or banner grabbing
- results depend on local firewall rules and network reachability
- use only in environments you are authorized to test

## Resume-Ready Bullet Points

- Built a threaded TCP port scanner with configurable targets, ranges, timeouts, and JSON output for lightweight network enumeration.
- Implemented concurrent socket-based scanning logic to identify open ports efficiently across lab or test environments.
- Refined a minimal proof-of-concept into a GitHub-ready security utility with clean CLI behavior, documentation, and reproducible validation workflow.
