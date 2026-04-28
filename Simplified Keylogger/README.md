# Simplified Keylogger

## Overview

`Simplified Keylogger` is a safe local keystroke-audit demo. It does not send email, does not exfiltrate captured data, and is intended only for transparent local input-audit checks in a controlled environment.

The project supports:

- local keyboard event capture for a fixed duration
- local JSON report generation
- deterministic `--demo` mode for validation without capturing real input
- clear local-only behavior

## Safety Model

This repository version:

- writes capture results to a local JSON file only
- does not send data to email, remote servers, or external services
- is intended for consent-based local testing only

## Tech Stack

- Python 3
- pynput for keyboard event capture
- Standard library: `argparse`, `json`, `time`, `pathlib`

## Project Structure

```text
Simplified Keylogger/
|-- keylogger.py
|-- README.md
`-- requirements.txt
```

## Requirements

```powershell
python -m pip install -r requirements.txt
```

## Usage

### Demo mode

Use this mode to validate the project without capturing live keyboard input:

```powershell
cd D:\Cybersec\Simplified Keylogger
python keylogger.py --demo --output demo_audit.json
```

### Timed local capture

```powershell
python keylogger.py --duration 10 --output audit_log.json
```

This starts a local capture for a fixed number of seconds and writes a JSON report with:

- total event count
- captured text representation

## Example Output

```json
{
  "event_count": 13,
  "captured_text": "Hello World\n[ENTER]"
}
```

## Capabilities

- keyboard event handling with `pynput`
- local audit logging
- bounded runtime and transparent output handling
