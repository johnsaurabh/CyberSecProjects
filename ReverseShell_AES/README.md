# ReverseShell_AES

## Overview

`ReverseShell_AES` is a safe encrypted remote task simulation. It uses an AES-protected client/server exchange over sockets with a fixed set of benign built-in tasks.

The project includes:

- AES-GCM protected socket communication
- framed JSON message exchange
- task dispatch from a controller to a client
- bounded client-side task execution
- clean local-lab validation

## Safety Model

This repository version does **not** implement a real reverse shell and does **not** execute arbitrary commands. The client only responds to a small safe task library:

- `collect_hostname`
- `collect_os`
- `collect_time`
- `heartbeat`

## Tech Stack

- Python 3
- PyCryptodome for AES-GCM encryption
- Standard library: `socket`, `json`, `argparse`, `struct`, `platform`

## Project Structure

```text
ReverseShell_AES/
|-- ReverseShell_Attacker.py
|-- ReverseShell_Client.py
|-- README.md
`-- requirements.txt
```

## Requirements

```powershell
python -m pip install -r requirements.txt
```

## Usage

### 1. Start the encrypted task server

```powershell
cd D:\Cybersec\ReverseShell_AES
python ReverseShell_Attacker.py --host 127.0.0.1 --port 4444 --task collect_hostname
```

### 2. Start the client

```powershell
python ReverseShell_Client.py --host 127.0.0.1 --port 4444
```

Expected behavior:

- the server sends an AES-GCM protected task message
- the client decrypts the task, executes a benign built-in action, and sends back an encrypted JSON result
- both sides print structured output locally

## Capabilities

- encrypted client/server communication over raw TCP sockets
- authenticated encryption using AES-GCM
- framed JSON messaging
- safe task dispatch architecture
