from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "path_length",
    "query_length",
    "dot_count",
    "hyphen_count",
    "digit_count",
    "subdomain_count",
    "uses_https",
    "has_ip_host",
    "has_at_symbol",
    "has_punycode",
    "has_suspicious_keyword",
    "entropy",
]

SUSPICIOUS_KEYWORDS = {
    "account",
    "auth",
    "bank",
    "billing",
    "bonus",
    "confirm",
    "crypto",
    "gift",
    "invoice",
    "login",
    "password",
    "pay",
    "prize",
    "recover",
    "secure",
    "signin",
    "unlock",
    "update",
    "verify",
    "wallet",
}

IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts: dict[str, int] = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    length = len(text)
    entropy = 0.0
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return round(entropy, 4)


def extract_features(url: str) -> dict[str, float]:
    parsed = urlparse(url)
    hostname = parsed.netloc.split("@")[-1].split(":")[0].lower()
    labels = [label for label in hostname.split(".") if label]
    keyword_hit = int(any(keyword in url.lower() for keyword in SUSPICIOUS_KEYWORDS))

    return {
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(parsed.path),
        "query_length": len(parsed.query),
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "digit_count": sum(char.isdigit() for char in url),
        "subdomain_count": max(0, len(labels) - 2),
        "uses_https": int(parsed.scheme == "https"),
        "has_ip_host": int(bool(IPV4_RE.match(hostname))),
        "has_at_symbol": int("@" in url),
        "has_punycode": int("xn--" in hostname),
        "has_suspicious_keyword": keyword_hit,
        "entropy": shannon_entropy(url),
    }


def extract_dataset_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, float | int | str]]:
    extracted: list[dict[str, float | int | str]] = []
    for row in rows:
        url = row["url"].strip()
        label = int(row["label"])
        features = extract_features(url)
        features["url"] = url
        features["label"] = label
        extracted.append(features)
    return extracted


def build_feature_dataset(input_path: Path, output_path: Path) -> int:
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = extract_dataset_rows(reader)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["url", *FEATURE_NAMES, "label"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract phishing-detection URL features without external services")
    parser.add_argument("--input", default="url_dataset.csv", help="Input CSV containing url,label columns")
    parser.add_argument("--output", default="enhanced_url_features.csv", help="Output feature CSV path")
    parser.add_argument("--url", help="Extract features for a single URL instead of processing a dataset")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print single URL features as JSON")
    args = parser.parse_args()

    if args.url:
        payload = extract_features(args.url)
        if args.pretty:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(json.dumps(payload, sort_keys=True))
        return

    row_count = build_feature_dataset(Path(args.input), Path(args.output))
    print(f"Extracted features for {row_count} URLs into {args.output}")


if __name__ == "__main__":
    main()
