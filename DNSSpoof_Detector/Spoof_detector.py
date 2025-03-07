from scapy.all import sniff, DNS, DNSQR, DNSRR
import dns.resolver
import csv
import os
import time
import requests
import whois
from termcolor import colored

# Cache for legitimate DNS records
legitimate_dns = {}

# File to store detected spoofing attempts
LOG_FILE = "dns_spoofing_log.csv"

def log_spoofing_attempt(query, detected_ip, correct_ips):
    """Logs DNS spoofing attempts to a CSV file."""
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, 'a', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Query', 'Fake IP', 'Expected IPs', 'WHOIS Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write header if file doesn't exist

        whois_info = get_whois_info(detected_ip)
        writer.writerow({
            'Timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'Query': query,
            'Fake IP': detected_ip,
            'Expected IPs': ', '.join(correct_ips),
            'WHOIS Info': whois_info
        })

def get_legitimate_dns_records(domain):
    """Dynamically fetches legitimate DNS records."""
    if domain in legitimate_dns:
        return legitimate_dns[domain]

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2  # Set a short timeout for faster checks
        resolver.lifetime = 2

        ips = [str(ip) for ip in resolver.resolve(domain, "A")]
        ipv6s = [str(ip) for ip in resolver.resolve(domain, "AAAA")]

        legitimate_dns[domain] = {"A": ips, "AAAA": ipv6s}
        return legitimate_dns[domain]
    except Exception:
        return {"A": [], "AAAA": []}

def get_whois_info(ip):
    """Performs a WHOIS lookup on the detected fake IP."""
    try:
        return str(whois.whois(ip))
    except Exception:
        return "WHOIS Lookup Failed"

def dns_spoofing_detector(packet):
    """Detects DNS spoofing by comparing responses with known good records."""
    if packet.haslayer(DNS) and packet.haslayer(DNSRR):
        dns = packet[DNS]
        if dns.qr == 1:  # It's a DNS response
            query = dns[DNSQR].qname.decode('utf-8').rstrip('.')
            legitimate_records = get_legitimate_dns_records(query)

            for answer in dns[DNSRR]:
                if answer.type == 1:  # A record (IPv4)
                    detected_ip = answer.rdata
                    if detected_ip not in legitimate_records["A"]:
                        alert = colored(f"[ALERT] DNS Spoofing Detected! Query: {query}, Fake IP: {detected_ip}", 'red')
                        print(alert)
                        log_spoofing_attempt(query, detected_ip, legitimate_records["A"])

                elif answer.type == 28:  # AAAA record (IPv6)
                    detected_ipv6 = answer.rdata
                    if detected_ipv6 not in legitimate_records["AAAA"]:
                        alert = colored(f"[ALERT] DNS Spoofing Detected! Query: {query}, Fake IPv6: {detected_ipv6}", 'red')
                        print(alert)
                        log_spoofing_attempt(query, detected_ipv6, legitimate_records["AAAA"])

def main():
    """Starts the DNS Spoofing Detector."""
    print(colored("[INFO] Starting Real-Time DNS Spoofing Detector...", 'blue'))
    print(colored("[INFO] Press Ctrl+C to stop.", 'blue'))
    time.sleep(2)

    sniff(filter="udp port 53", prn=dns_spoofing_detector, store=False)

if __name__ == '__main__':
    main()
