from __future__ import annotations

import argparse
import json
import threading
import time
from pathlib import Path
from typing import Any

from pynput import keyboard


captured_events: list[str] = []
capture_lock = threading.Lock()


def normalize_key(key: Any) -> str:
    try:
        if key.char is not None:
            return key.char
    except AttributeError:
        pass

    if key == keyboard.Key.space:
        return " "
    if key == keyboard.Key.enter:
        return "\n"
    if key == keyboard.Key.tab:
        return "[TAB]"
    if key == keyboard.Key.backspace:
        return "[BACKSPACE]"
    return f"[{key}]"


def on_press(key: Any) -> None:
    with capture_lock:
        captured_events.append(normalize_key(key))


def write_report(output_path: Path) -> dict[str, Any]:
    with capture_lock:
        payload = {
            "event_count": len(captured_events),
            "captured_text": "".join(captured_events),
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def run_capture(duration: float, output_path: Path) -> dict[str, Any]:
    print("Starting local input audit.")
    print(f"Capture duration: {duration} seconds")
    print(f"Output file: {output_path}")
    print("This tool writes locally only and does not send data anywhere.")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    try:
        time.sleep(duration)
    finally:
        listener.stop()
        listener.join(timeout=2)

    payload = write_report(output_path)
    print(json.dumps(payload, indent=2))
    return payload


def run_demo(output_path: Path) -> dict[str, Any]:
    demo_events = ["H", "e", "l", "l", "o", " ", "W", "o", "r", "l", "d", "\n", "[ENTER]"]
    with capture_lock:
        captured_events.clear()
        captured_events.extend(demo_events)
    payload = write_report(output_path)
    print(json.dumps(payload, indent=2))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Safe local keystroke audit demo")
    parser.add_argument("--duration", type=float, default=10.0, help="Capture duration in seconds")
    parser.add_argument("--output", default="audit_log.json", help="Local JSON report path")
    parser.add_argument("--demo", action="store_true", help="Write a deterministic demo report without capturing real input")
    args = parser.parse_args()

    output_path = Path(args.output)
    if args.demo:
        run_demo(output_path)
        return

    run_capture(args.duration, output_path)


if __name__ == "__main__":
    main()
