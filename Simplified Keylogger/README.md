# Simplified Keylogger

## Overview

`Simplified Keylogger` has been converted into a safe local keystroke-audit demo. It no longer sends email, does not exfiltrate captured data, and is intended only for transparent local input-audit demonstrations in a controlled environment.

The project now supports:

- local keyboard event capture for a fixed duration
- local JSON report generation
- deterministic `--demo` mode for validation without capturing real input
- clear, public-repository-safe behavior

## Safety Model

This repository version:

- writes capture results to a local JSON file only
- does not send data to email, remote servers, or external services
- is intended for consent-based local testing only

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

## What The Project Demonstrates

- keyboard event handling with `pynput`
- local audit logging
- safe refactoring of an unsafe prototype
- bounded runtime and transparent output handling

## Resume-Ready Bullet Points

- Built a safe local keystroke-audit demo that captures input for a fixed duration and writes structured JSON reports without any remote exfiltration.
- Implemented keyboard event normalization, local file reporting, and a deterministic demo mode for reproducible validation in a controlled lab setting.
- Refactored an unsafe proof-of-concept into a GitHub-ready input-audit utility suitable for secure coding and endpoint-monitoring discussions.
