# PhishingDetector

## Overview

`PhishingDetector` is a lightweight URL phishing-detection project designed to be runnable locally without heavy ML frameworks or external threat-intelligence dependencies. It extracts security-relevant lexical URL features, trains a compact logistic-regression classifier, and exposes a local HTTP API for scoring suspicious links.

The implementation is self-contained and can be validated locally.

## Capabilities

- URL feature engineering for phishing detection
- classification workflow from labeled dataset to trained model
- local API exposure for real-time scoring
- clean CLI-based security tooling
- documentation and reproducible execution

## Tech Stack

- Python 3
- Standard library: `argparse`, `csv`, `http.server`, `json`, `math`, `urllib`
- Lightweight logistic-regression implementation stored as JSON model parameters

## Project Structure

```text
PhishingDetector/
|-- phish_guard_lstm.py
|-- phish_sense_feature_extractor.py
|-- url_dataset.csv
|-- requirements.txt
`-- README.md
```

## Implementation Notes

The historical file names are preserved for repository continuity:

- `phish_sense_feature_extractor.py` extracts URL features into a CSV dataset.
- `phish_guard_lstm.py` trains and serves a lightweight logistic-regression classifier.

This implementation is:

- runnable on a clean Python installation
- easy to test locally
- suitable for local validation

## Features Used For Detection

The feature extractor computes:

- URL length
- hostname length
- path length
- query length
- number of dots
- number of hyphens
- number of digits
- subdomain count
- whether HTTPS is used
- whether the host is an IPv4 address
- whether the URL contains an `@` symbol
- whether the hostname contains punycode
- whether suspicious keywords are present
- Shannon entropy of the URL string

These features are useful for flagging common phishing traits such as excessive complexity, misleading host structures, insecure transport, credential-themed wording, and direct-IP links.

## Dataset

The included `url_dataset.csv` contains a small labeled sample set with:

- `0` for legitimate URLs
- `1` for phishing-like URLs

The dataset is intended for local validation, not production-grade detection accuracy.

## Requirements

No third-party Python packages are required for the current implementation.

## Usage

### 1. Extract features from the dataset

```powershell
cd D:\Cybersec\PhishingDetector
python phish_sense_feature_extractor.py --input url_dataset.csv --output enhanced_url_features.csv
```

### 2. Train the model

```powershell
cd D:\Cybersec\PhishingDetector
python phish_guard_lstm.py --train
```

Expected output is a JSON summary that includes:

- model path
- number of training rows
- training accuracy

This produces `phishing_model.json`.

### 3. Score a single URL

```powershell
cd D:\Cybersec\PhishingDetector
python phish_guard_lstm.py --url "http://paypal.verify-account-login.com/reset"
```

Example response:

```json
{
  "features": {
    "digit_count": 0,
    "dot_count": 3,
    "entropy": 4.3232,
    "has_at_symbol": 0,
    "has_ip_host": 0,
    "has_punycode": 0,
    "has_suspicious_keyword": 1,
    "hostname_length": 32,
    "hyphen_count": 2,
    "path_length": 6,
    "query_length": 0,
    "subdomain_count": 2,
    "url_length": 39,
    "uses_https": 0
  },
  "phishing_probability": 0.93,
  "url": "http://paypal.verify-account-login.com/reset",
  "verdict": "phishing"
}
```

### 4. Run the local API

```powershell
cd D:\Cybersec\PhishingDetector
python phish_guard_lstm.py --api --host 127.0.0.1 --port 5000
```

### 5. Test the API

```powershell
curl -X POST http://127.0.0.1:5000/detect -H "Content-Type: application/json" -d "{\"url\":\"http://secure-banking-confirmation.example.net/login\"}"
```

### 6. Health check

```powershell
curl http://127.0.0.1:5000/health
```

## Example Workflow

1. Build the feature dataset.
2. Train the lightweight model.
3. Score URLs from the CLI.
4. Run the API for local integration or demo use.

## Security Limitations

This project is not a production anti-phishing stack. Known limitations:

- uses a small local dataset only
- relies on lexical URL features rather than rendered page analysis
- does not fetch live page content
- does not use reputation feeds or certificate inspection
- does not include browser integration

## Recommended Improvements

- add a larger labeled dataset
- add domain-age or certificate-age enrichment as optional modules
- add URL normalization and redirect-chain handling
- add confusion-matrix reporting and test splits
- add containerized deployment for the local API
