# Portscanner

## Overview

`Portscanner` is a lightweight threaded TCP port scanner for local lab validation and basic network enumeration. It supports:

- configurable targets
- custom port lists and ranges
- timeout tuning
- structured JSON output
- reproducible local validation

The scanner is intentionally small and focused on local lab use.

## Capabilities

- TCP port reachability testing
- threaded network scanning
- CLI-based security utility design
- human-readable and machine-readable output modes

## Tech Stack

- Python 3
- Standard library: `socket`, `threading`, `argparse`, `json`, `queue`

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
