import re
import whois
import requests
import ssl
import socket
import datetime
import pandas as pd
from urllib.parse import urlparse
from collections import Counter

# VirusTotal API Key (replace with your own)
VT_API_KEY = "your_virustotal_api_key"

def get_ssl_info(url):
    """Check SSL certificate validity."""
    try:
        hostname = urlparse(url).netloc
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
        conn.connect((hostname, 443))
        cert = conn.getpeercert()
        return (datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y GMT") - datetime.datetime.now()).days
    except:
        return -1  # Invalid SSL

def get_whois_age(domain):
    """Get domain age from WHOIS."""
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        age = (datetime.datetime.now() - creation_date).days
        return age
    except:
        return -1

def check_virustotal(url):
    """Query VirusTotal API."""
    headers = {"x-apikey": VT_API_KEY}
    response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url}", headers=headers)
    return 1 if response.status_code == 200 and response.json()["data"]["attributes"]["last_analysis_stats"]["malicious"] > 0 else 0

def extract_features(url):
    """Feature engineering for phishing detection."""
    parsed = urlparse(url)
    domain = parsed.netloc
    return [
        len(url), len(domain),
        url.count("-"), url.count("@"),
        len(re.findall(r"\d+", url)), parsed.netloc.count("."),
        get_ssl_info(url), get_whois_age(domain), check_virustotal(url)
    ]

# Apply feature extraction
df = pd.read_csv("url_dataset.csv")
df_features = df["url"].apply(lambda x: extract_features(x)).apply(pd.Series)
df_features["label"] = df["label"]

df_features.to_csv("enhanced_url_features.csv", index=False)
print("Feature extraction completed!")
