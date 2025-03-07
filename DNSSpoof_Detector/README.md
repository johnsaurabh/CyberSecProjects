DNS Spoofing Detection Tool

Overview:
DNS spoofing (also known as DNS cache poisoning) is a cyber attack where a malicious DNS response is used to redirect users to fake websites instead of the intended legitimate domain. This tool captures DNS traffic in real-time and detects spoofing attempts by comparing responses with legitimate DNS records.

Features:

Real-time DNS Packet Sniffing (Using Scapy)

Dynamic DNS Verification (Uses dnspython to fetch legitimate records)

Logs Spoofing Attempts to a CSV file

WHOIS Lookup for Malicious IPs

IPv4 and IPv6 Detection (Handles A and AAAA records)

Exception Handling for Stability

Extensible for Additional Security Features

Installation:

Clone the Repository:
git clone 
cd 

Install Dependencies:
pip install scapy dnspython termcolor whois requests

Run the DNS Spoofing Detector:
sudo python3 dns_spoof_detector.py

(Note: Root access is required for sniffing network packets)

How It Works:

The tool captures live DNS packets on UDP port 53.

It extracts domain queries and their corresponding responses.

It dynamically fetches legitimate DNS records and compares them with the response.

If a mismatched IP is detected, the tool:

Prints an alert on the screen.

Logs the attack details in a CSV file.

Performs a WHOIS lookup to gather information about the attacker’s IP address.

Example Output:
[INFO] Starting Real-Time DNS Spoofing Detector...
[INFO] Press Ctrl+C to stop.
[ALERT] DNS Spoofing Detected! Query: google.com, Fake IP: 192.168.1.100
[ALERT] DNS Spoofing Detected! Query: facebook.com, Fake IPv6: 2607:f8b0:4005:808::200e

The log entry is saved in dns_spoofing_log.csv with the following details:
Timestamp | Query | Fake IP | Expected IPs | WHOIS Info
2025-03-07 14:30:12 | google.com | 192.168.1.100 | 142.250.74.206 | WHOIS Lookup Data

Configuration:
Modify detection behavior by adjusting parameters in the script:

Update the log file path in LOG_FILE = "dns_spoofing_log.csv"

Adjust the DNS lookup timeout in the resolver settings:
resolver.timeout = 2
resolver.lifetime = 2

Future Enhancements:

Email notifications for detected spoofing attempts

Integration with VirusTotal API for IP reputation checks

GUI for easier management and visualization of logs


Highlights:

Provides real-world DNS attack detection techniques

Demonstrates practical skills in network security and packet analysis

Uses industry-relevant tools such as Scapy and WHOIS for threat intelligence

Author:
Developed by John Saurabh Battu