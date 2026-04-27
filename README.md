# CyberSec Research Projects

A collection of offensive and defensive security tools built for research, education, and authorized lab environments. Each project targets a specific domain of security engineering — from kernel-level persistence to network traffic analysis to ML-based threat detection.

All tools are built for **educational purposes and controlled lab environments only**. No tool in this repository is intended for use against systems without explicit authorization.

---

## Projects

### Offensive Security Research

| Project | Language | Description |
|---------|----------|-------------|
| [StealthyRootkit](./StealthyRootkit/) | C | Kernel-level LKM rootkit demonstrating syscall hooking, process hiding, and file system stealth. Built to understand how kernel-level persistence actually works at the syscall table level. |
| [MalwareC2Server](./MalwareC2Server/) | Python | Command-and-control simulation framework modeling real-world attacker infrastructure — server/client comms, task queuing, and execution flows. Built for red team simulation and C2 detection research. |
| [ReverseShell_AES](./ReverseShell_AES/) | Python | Encrypted reverse shell using AES to understand how defenders can detect (or miss) encrypted callback channels. Used for testing network monitoring and DPI setups. |
| [Simplified Keylogger](./SimplifiedKeylogger/) | Python | Basic keylogger demonstrating OS-level input interception. Built as part of endpoint detection research — understanding what keyloggers do is prerequisite to catching them. |

### Threat Detection & Defense

| Project | Language | Description |
|---------|----------|-------------|
| [Tartarus Gate](https://github.com/johnsaurabh/Tartarus_Gate) | Rust · Python | Multi-layer security platform. WAF (Iron Veil) + ML-based malware classification (BloodHound) + threat neutralization (Reaper). Moved to a standalone repo. |
| [PhishingDetector](./PhishingDetector/) | Python | URL and content analysis pipeline for phishing site classification. Combines heuristic rules with ML-based scoring across multiple signal types. |
| [DNSSpoof_Detector](./DNSSpoof_Detector/) | Python | Network monitor that detects DNS spoofing and cache poisoning attempts in real time by analyzing response consistency and TTL anomalies. |

### Network & Recon Tools

| Project | Language | Description |
|---------|----------|-------------|
| [Portscanner](./Portscanner/) | Python | Multi-threaded TCP/UDP port scanner with service fingerprinting and configurable scan profiles. |
| [ViperFang](https://github.com/johnsaurabh/ViperFang) | Python | Network traffic analysis and anomaly detection tool. Moved to standalone repo. |
| [Nemesis](https://github.com/johnsaurabh/Nemesis) | Python | Automated vulnerability scanning and enumeration framework. Moved to standalone repo. |

### Steganography & Covert Channels

| Project | Language | Description |
|---------|----------|-------------|
| [SteganographyDetector](./SteganographyDetector/) | Python | Detection tool for LSB and frequency-domain steganography in image and audio files. Counterpart to covert channel research. |

---

## Stack

`Python` `C` `Linux Kernel (LKM)` `Syscall Hooking` `Scapy` `Scikit-learn` `Socket Programming` `AES Encryption` `Multi-threading`

---

## Methodology

These projects were built progressively — each one targeting a specific gap in my understanding of a security domain. The pattern is consistent: build the offensive tool to understand it, then build the detection mechanism to catch it.

The rootkit taught me more about how AV evasion works than any blog post. The C2 server taught me what beaconing patterns look like on the wire. The phishing detector forced me to think about what actually differentiates a convincing phishing page from a legitimate one at a feature level.

Security is easier to defend when you've built the attack.

---

## Ethics & Usage

- All tools are built in isolated lab environments (local VMs, private networks)
- No tool has been used against systems without authorization
- Source code is shared for educational purposes — understanding attack techniques is foundational to building effective defenses
- HackTheBox, CTF environments, and personal lab infrastructure are the intended deployment targets

---

## Related

- [Tartarus Gate](https://github.com/johnsaurabh/Tartarus_Gate) — The production-grade evolution of this research: a full security platform
- [Vehicle Threat Model](https://github.com/johnsaurabh/vehicle-threat-model) — Applying threat modeling methodology to automotive ECU architecture
- [Automotive Security Demo](https://github.com/johnsaurabh/automotive-secure-communication-demo) — Secure communication implementation derived from the threat model

---

<div align="center">
  <sub><a href="https://github.com/johnsaurabh">johnsaurabh</a> · <a href="https://johnsaurabh.com">johnsaurabh.com</a> · <a href="https://app.hackthebox.com/users/ExploitLord">HackTheBox: ExploitLord</a></sub>
</div>
