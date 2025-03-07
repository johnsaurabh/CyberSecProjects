# AI-Powered Phishing Detection System

## Overview
This project is an AI-driven phishing detection system that identifies malicious URLs using machine learning and deep learning (LSTM). It extracts key URL features, checks WHOIS and SSL details, integrates the VirusTotal API, and provides a real-time API for phishing classification.

## Features
- Uses deep learning (LSTM) for phishing detection
- Extracts WHOIS, SSL, URL entropy, and other features
- Integrates VirusTotal API for additional security validation
- Provides a real-time Flask API for phishing classification
- Optimized for speed and scalability

## Project Structure
- `phish_sense_feature_extractor.py` - Extracts WHOIS, SSL, URL entropy, and VirusTotal API features
- `phish_guard_lstm.py` - Trains the LSTM model and provides the real-time Flask API
- `requirements.txt` - Lists required dependencies
- `README.md` - Project documentation

## Installation Guide
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AI-Powered-Phishing-Detection.git
   cd AI-Powered-Phishing-Detection
   ```
2. Install dependencies:
   
   pip install -r requirements.txt


## Usage
1. Extract URL Features:
 
   python phish_sense_feature_extractor.py

2. Train the LSTM Model:
   
   python phish_guard_lstm.py --train
 
3. Run the Phishing Detection API:

   python phish_guard_lstm.py --api

4. Test the API with a URL:

   curl -X POST http://127.0.0.1:5000/detect -H "Content-Type: application/json" -d '{"url": "http://suspicious-site.com"}'
 

## Technical Details
### Feature Extraction
- **WHOIS Data:** Extracts domain age and registrar details
- **SSL Certificate Validity:** Checks whether the site has a valid SSL certificate
- **URL Entropy:** Analyzes randomness in the URL structure
- **VirusTotal API:** Cross-checks against a known phishing database

### LSTM Model
- **Input:** URL feature vectors
- **Architecture:** Two LSTM layers and Dense layers
- **Output:** Probability of phishing (0 = Safe, 1 = Malicious)

### Flask API
- **Endpoint:** `/detect`
- **Input:** JSON with URL
- **Output:** Classification as phishing or legitimate

## References
- [OpenPhish Database](https://openphish.com/)
- [VirusTotal API](https://developers.virustotal.com/reference)

## Security Considerations
- Ensure API key security when using VirusTotal
- Deploy on a secured server to prevent abuse
- Regularly update the phishing dataset to improve accuracy

## Author
John Saurabh Battu  

