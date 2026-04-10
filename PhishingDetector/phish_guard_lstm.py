from __future__ import annotations

import argparse
import csv
import json
import math
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from phish_sense_feature_extractor import FEATURE_NAMES, build_feature_dataset, extract_features


MODEL_PATH = Path("phishing_model.json")


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def load_feature_rows(feature_csv_path: Path) -> tuple[list[list[float]], list[int]]:
    with feature_csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        samples: list[list[float]] = []
        labels: list[int] = []
        for row in reader:
            samples.append([float(row[name]) for name in FEATURE_NAMES])
            labels.append(int(row["label"]))
    return samples, labels


def train_model(feature_csv_path: Path, model_path: Path, epochs: int = 600, learning_rate: float = 0.15) -> dict[str, Any]:
    samples, labels = load_feature_rows(feature_csv_path)
    if not samples:
        raise ValueError("Feature dataset is empty")

    feature_count = len(FEATURE_NAMES)
    means = [sum(sample[idx] for sample in samples) / len(samples) for idx in range(feature_count)]
    stds = []
    for idx in range(feature_count):
        variance = sum((sample[idx] - means[idx]) ** 2 for sample in samples) / len(samples)
        stds.append(math.sqrt(variance) or 1.0)

    normalized = [
        [(sample[idx] - means[idx]) / stds[idx] for idx in range(feature_count)]
        for sample in samples
    ]

    weights = [0.0] * feature_count
    bias = 0.0

    for _ in range(epochs):
        weight_gradients = [0.0] * feature_count
        bias_gradient = 0.0
        for sample, label in zip(normalized, labels):
            prediction = sigmoid(sum(weight * value for weight, value in zip(weights, sample)) + bias)
            error = prediction - label
            for idx in range(feature_count):
                weight_gradients[idx] += error * sample[idx]
            bias_gradient += error

        sample_count = len(normalized)
        for idx in range(feature_count):
            weights[idx] -= learning_rate * (weight_gradients[idx] / sample_count)
        bias -= learning_rate * (bias_gradient / sample_count)

    predictions = [1 if sigmoid(sum(weight * value for weight, value in zip(weights, sample)) + bias) >= 0.5 else 0 for sample in normalized]
    accuracy = sum(int(pred == label) for pred, label in zip(predictions, labels)) / len(labels)

    model = {
        "model_type": "lightweight_logistic_regression",
        "feature_names": FEATURE_NAMES,
        "weights": weights,
        "bias": bias,
        "means": means,
        "stds": stds,
        "training_rows": len(labels),
        "training_accuracy": round(accuracy, 4),
    }
    model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")
    return model


def load_model(model_path: Path) -> dict[str, Any]:
    return json.loads(model_path.read_text(encoding="utf-8"))


def score_url(url: str, model: dict[str, Any]) -> dict[str, Any]:
    feature_map = extract_features(url)
    values = [float(feature_map[name]) for name in model["feature_names"]]
    normalized = [
        (values[idx] - model["means"][idx]) / (model["stds"][idx] or 1.0)
        for idx in range(len(values))
    ]
    probability = sigmoid(sum(weight * value for weight, value in zip(model["weights"], normalized)) + model["bias"])
    verdict = "phishing" if probability >= 0.5 else "legitimate"
    return {
        "url": url,
        "verdict": verdict,
        "phishing_probability": round(probability, 4),
        "features": feature_map,
    }


def make_handler(model_path: Path):
    class DetectionHandler(BaseHTTPRequestHandler):
        def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/detect":
                self._send_json(404, {"error": "Not Found"})
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            try:
                payload = json.loads(raw_body.decode("utf-8"))
                url = payload["url"]
            except (KeyError, json.JSONDecodeError, UnicodeDecodeError):
                self._send_json(400, {"error": "Request body must be JSON and include a url field"})
                return

            result = score_url(url, load_model(model_path))
            self._send_json(200, result)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send_json(200, {"status": "ok"})
                return
            self._send_json(404, {"error": "Not Found"})

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return DetectionHandler


def ensure_feature_dataset(dataset_path: Path, feature_path: Path) -> None:
    if feature_path.exists():
        return
    build_feature_dataset(dataset_path, feature_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train, score, or serve a lightweight phishing-detection classifier. The historical filename is preserved for repo continuity."
    )
    parser.add_argument("--train", action="store_true", help="Train the model from the dataset")
    parser.add_argument("--api", action="store_true", help="Run the local HTTP detection API")
    parser.add_argument("--url", help="Score a single URL using the trained model")
    parser.add_argument("--dataset", default="url_dataset.csv", help="Raw labeled URL dataset path")
    parser.add_argument("--features", default="enhanced_url_features.csv", help="Extracted feature dataset path")
    parser.add_argument("--model", default=str(MODEL_PATH), help="Model JSON path")
    parser.add_argument("--host", default="127.0.0.1", help="API bind address")
    parser.add_argument("--port", type=int, default=5000, help="API port")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    feature_path = Path(args.features)
    model_path = Path(args.model)

    if args.train:
        ensure_feature_dataset(dataset_path, feature_path)
        model = train_model(feature_path, model_path)
        print(json.dumps({
            "status": "trained",
            "model_path": str(model_path),
            "training_rows": model["training_rows"],
            "training_accuracy": model["training_accuracy"],
        }, indent=2))
        return

    if args.url:
        if not model_path.exists():
            ensure_feature_dataset(dataset_path, feature_path)
            train_model(feature_path, model_path)
        print(json.dumps(score_url(args.url, load_model(model_path)), indent=2, sort_keys=True))
        return

    if args.api:
        if not model_path.exists():
            ensure_feature_dataset(dataset_path, feature_path)
            train_model(feature_path, model_path)
        server = ThreadingHTTPServer((args.host, args.port), make_handler(model_path))
        print(f"Phishing detection API listening on http://{args.host}:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
