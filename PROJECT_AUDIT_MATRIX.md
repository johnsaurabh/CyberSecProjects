# CyberSec Projects Audit Matrix

## Purpose

This document tracks the audit status of legacy projects in the `CyberSecProjects` repository so they can be repaired, validated, and updated in place through follow-up commits. It excludes the two newly created portfolio projects and the three folders intentionally deferred for now.

## In Scope

- `DNSSpoof_Detector`
- `MalwareC2Server`
- `PhishingDetector`
- `Portscanner`
- `ReverseShell_AES`
- `Simplified Keylogger`
- `StealthyRootkit`
- `SteganographyDetector`

## Excluded For Now

- `AutomotiveSecureComm`
- `vehicle-threat-model`
- `ViperFang`
- `Nemesis`
- `tartarusGate`

## Status Legend

- `Working`: validated and appears operational for its intended scope
- `Prototype`: concept is present, but missing dependencies, assets, integration, or runtime validation
- `Faulty`: significant implementation or design issues prevent the project from being considered working
- `Unsafe To Run`: offensive or system-level tooling that was reviewed primarily through static analysis rather than live execution

## Audit Matrix

| Project | Type | Status | Safe Validation Performed | Primary Issues | Fix Priority |
|---|---|---|---|---|---|
| `Portscanner` | Network utility | Working | Syntax check, contained localhost functional test, and JSON output validation | Lightweight TCP connect scanner only; no service fingerprinting or banner grabbing | Completed |
| `DNSSpoof_Detector` | Network security monitor | Working | Syntax check, demo PCAP generation, offline PCAP analysis, and CSV finding export validation | Baseline-driven detection requires curated expected records; encrypted DNS is out of scope | Completed |
| `PhishingDetector` | URL phishing detection | Working | Syntax check, feature extraction, model training, CLI scoring, and local API validation | Demo dataset only; lexical features only; no live reputation or content analysis | Completed |
| `SteganographyDetector` | Image forensics utility | Working | Syntax check, demo asset generation, decode validation, compare validation, and image analysis validation | Baseline comparison is strongest when the original cover image is available; heuristic analysis remains non-authoritative | Completed |
| `MalwareC2Server` | Safe C2 simulation | Working | Syntax check and end-to-end local validation of registration, task queueing, polling, and reporting | Public-safe simulation only; does not execute arbitrary commands by design | Completed |
| `ReverseShell_AES` | Encrypted reverse shell demo | Prototype / Unsafe To Run | Syntax check and static review only | Placeholder attacker host, undeclared crypto dependency, fixed IV, incomplete deployment flow | High |
| `Simplified Keylogger` | Endpoint surveillance demo | Prototype / Unsafe To Run | Syntax check and static review only | Placeholder credentials, depends on `pynput`, impractical Gmail SMTP flow, not suitable as a verified working deliverable | High |
| `StealthyRootkit` | Linux kernel rootkit demo | Faulty / Unsafe To Run | Static review only | README does not match files present, missing `Makefile`, unsafe and incomplete syscall hook logic, unload path incorrect | Critical |

## Evidence Summary By Project

### 1. Portscanner

- File: `Portscanner/portscanner.py`
- Result: passed `python -m py_compile`
- Result: succeeded in a contained localhost test against a temporary listener
- Result: JSON output mode validated successfully
- Findings:
  - project now includes proper CLI argument parsing, timeout tuning, and structured output
  - the original interactive-only proof of concept was upgraded into a cleaner utility
- Conclusion: repaired and verified as working

### 2. DNSSpoof_Detector

- Files: `DNSSpoof_Detector/Spoof_detector.py`, `DNSSpoof_Detector/README.md`
- Result: passed `python -m py_compile`
- Result: demo PCAP generation succeeded
- Result: offline PCAP analysis detected spoofed `A` and `AAAA` answers correctly
- Result: CSV findings export succeeded
- Findings:
  - project was rebuilt around a safer offline-analysis workflow with optional live sniffing
  - baseline DNS expectations are now supplied from a reproducible JSON file
  - sample PCAP and findings artifacts can be generated for local validation and GitHub presentation
- Conclusion: repaired and verified as working

### 3. PhishingDetector

- Files: `PhishingDetector/phish_guard_lstm.py`, `PhishingDetector/phish_sense_feature_extractor.py`, `PhishingDetector/README.md`
- Result: passed `python -m py_compile`
- Result: feature extraction completed successfully against the included dataset
- Result: model training completed successfully and produced `phishing_model.json`
- Result: single-URL CLI scoring completed successfully
- Result: local API validation succeeded with `/health` and `/detect`
- Findings:
  - project was rebuilt into a self-contained implementation using standard-library-only feature extraction and a lightweight logistic-regression classifier
  - the original nonfunctional LSTM prototype and broken documentation were replaced in place
  - the project now includes an included dataset, requirements file, reproducible training flow, and working local HTTP API
- Conclusion: repaired and verified as working

### 4. SteganographyDetector

- File: `SteganographyDetector/Detector.py`
- Result: passed `python -m py_compile`
- Result: demo workflow generated reproducible cover, stego, and overlay images
- Result: decode command successfully recovered the embedded message
- Result: compare command successfully quantified and visualized modified pixels
- Result: analyze command successfully summarized LSB distribution
- Findings:
  - project was rebuilt as a working LSB encode/decode and baseline-comparison utility
  - a 32-bit length prefix is now used for reliable payload recovery
  - demo samples can be generated and rendered directly on GitHub
- Conclusion: repaired and verified as working

### 5. MalwareC2Server

- Files: `MalwareC2Server/C2Server.py`, `MalwareC2Server/MalwareClient.py`
- Result: passed `python -m py_compile`
- Result: local server startup succeeded
- Result: agent registration, task queueing, polling, and report retrieval succeeded end to end
- Findings:
  - project was refactored into a safe C2 simulation with bounded benign task types
  - arbitrary shell execution was removed to keep the repository publishable and defensible
  - the project now includes operator task queueing and structured report retrieval
- Conclusion: repaired and verified as a working safe simulation

### 6. ReverseShell_AES

- Files: `ReverseShell_AES/ReverseShell_Attacker.py`, `ReverseShell_AES/ReverseShell_Client.py`
- Result: passed `python -m py_compile`
- Findings:
  - client uses placeholder `"attacker-ip"`
  - undeclared dependency on `Crypto` / PyCryptodome
  - fixed IV is reused for all AES-CBC messages
  - no packaging, documentation, or safe test harness exists
- Conclusion: prototype only, not verified runnable

### 7. Simplified Keylogger

- File: `Simplified Keylogger/keylogger.py`
- Result: passed `python -m py_compile`
- Findings:
  - placeholder email and password values are hardcoded
  - Gmail SMTP password flow is not a reliable modern delivery design
  - no configuration, consent model, or containment strategy exists
- Conclusion: not a defensible “working project” in current form

### 8. StealthyRootkit

- Files: `StealthyRootkit/BackdoorUser.c`, `StealthyRootkit/SyscallHook.c`, `StealthyRootkit/README.md`
- Result: static review only
- Findings:
  - README references `rootkit.c` and `Makefile`, but neither exists
  - actual code is split across two files with no build system
  - syscall table patching is incomplete and unsafe
  - unload path incorrectly calls `kfree` on a saved function pointer
  - code does not implement the full behavior claimed by the README
- Conclusion: faulty and highest repair risk in the current batch

## Recommended Fix Order

1. `ReverseShell_AES`
2. `Simplified Keylogger`
3. `StealthyRootkit`

## Rationale For Fix Order

- Start with projects that can be turned into clean, defensible portfolio deliverables without unsafe execution requirements.
- Leave offensive or kernel-level tooling for later because those need tighter scope, safer framing, and more careful validation.
- Fixing the higher-value defensive projects first will raise overall repo quality faster.

## Repository Update Strategy

All repaired projects should be updated in the existing repository:

- Repository: `https://github.com/johnsaurabh/CyberSecProjects`
- Branch: `main`
- Rule: do not create new repositories for these legacy projects
- Process: repair locally inside the existing folder, validate, commit, and push as incremental final commits

## Next Step

Use this matrix as the source of truth while fixing projects one by one. `PhishingDetector`, `SteganographyDetector`, `DNSSpoof_Detector`, `Portscanner`, and `MalwareC2Server` have now been repaired and validated, so the next best candidate is `ReverseShell_AES`.
