from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path
from typing import Iterable

from PIL import Image


LENGTH_PREFIX_BITS = 32


def text_to_bits(message: str) -> str:
    payload = message.encode("utf-8")
    length_prefix = f"{len(payload):032b}"
    payload_bits = "".join(f"{byte:08b}" for byte in payload)
    return length_prefix + payload_bits


def bits_to_text(payload_bits: str) -> str:
    message_bytes = bytearray()
    for index in range(0, len(payload_bits), 8):
        byte = payload_bits[index:index + 8]
        if len(byte) == 8:
            message_bytes.append(int(byte, 2))
    return message_bytes.decode("utf-8")


def image_capacity_bits(image: Image.Image) -> int:
    width, height = image.size
    return width * height * 3


def encode_lsb(cover_path: Path, message: str, output_path: Path) -> dict[str, int]:
    image = Image.open(cover_path).convert("RGB")
    bits = text_to_bits(message)
    capacity = image_capacity_bits(image)
    if len(bits) > capacity:
        raise ValueError(f"Message requires {len(bits)} bits, but image capacity is {capacity} bits")

    pixels = image.load()
    bit_index = 0
    modified_channels = 0
    width, height = image.size

    for y in range(height):
        for x in range(width):
            channels = list(pixels[x, y])
            for idx in range(3):
                if bit_index >= len(bits):
                    pixels[x, y] = tuple(channels)
                    image.save(output_path)
                    return {
                        "payload_bits": len(bits),
                        "modified_channels": modified_channels,
                        "capacity_bits": capacity,
                    }
                target_bit = int(bits[bit_index])
                original_value = channels[idx]
                channels[idx] = (original_value & ~1) | target_bit
                if channels[idx] != original_value:
                    modified_channels += 1
                bit_index += 1
            pixels[x, y] = tuple(channels)

    image.save(output_path)
    return {
        "payload_bits": len(bits),
        "modified_channels": modified_channels,
        "capacity_bits": capacity,
    }


def read_embedded_bits(image: Image.Image, bit_count: int) -> str:
    pixels = image.load()
    width, height = image.size
    bits: list[str] = []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            for value in (r, g, b):
                bits.append(str(value & 1))
                if len(bits) == bit_count:
                    return "".join(bits)
    raise ValueError("Image does not contain enough data for the requested bit count")


def decode_lsb(image_path: Path) -> dict[str, str | int]:
    image = Image.open(image_path).convert("RGB")
    prefix_bits = read_embedded_bits(image, LENGTH_PREFIX_BITS)
    message_length_bytes = int(prefix_bits, 2)
    payload_bit_count = message_length_bytes * 8
    payload_bits = read_embedded_bits(image, LENGTH_PREFIX_BITS + payload_bit_count)[LENGTH_PREFIX_BITS:]
    message = bits_to_text(payload_bits)
    return {
        "message": message,
        "message_length_bytes": message_length_bytes,
        "payload_bits": payload_bit_count,
    }


def compare_images(cover_path: Path, suspect_path: Path, output_path: Path) -> dict[str, float | int]:
    cover = Image.open(cover_path).convert("RGB")
    suspect = Image.open(suspect_path).convert("RGB")
    if cover.size != suspect.size:
        raise ValueError("Cover and suspect images must have the same dimensions")

    cover_pixels = cover.load()
    suspect_pixels = suspect.load()
    overlay = Image.new("RGB", cover.size)
    overlay_pixels = overlay.load()

    width, height = cover.size
    changed_pixels = 0
    changed_channels = 0

    for y in range(height):
        for x in range(width):
            cover_rgb = cover_pixels[x, y]
            suspect_rgb = suspect_pixels[x, y]
            channel_deltas = [int((cover_rgb[idx] & 1) != (suspect_rgb[idx] & 1)) for idx in range(3)]
            delta_count = sum(channel_deltas)
            changed_channels += delta_count
            if delta_count:
                changed_pixels += 1
                overlay_pixels[x, y] = (255, 0, 0)
            else:
                grayscale = sum(suspect_rgb) // 3
                overlay_pixels[x, y] = (grayscale, grayscale, grayscale)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(output_path)
    total_pixels = width * height
    return {
        "changed_pixels": changed_pixels,
        "changed_channels": changed_channels,
        "changed_pixel_ratio": round(changed_pixels / total_pixels, 4),
    }


def analyze_image(image_path: Path) -> dict[str, float | int]:
    image = Image.open(image_path).convert("RGB")
    pixels = image.load()
    width, height = image.size
    lsb_values: list[int] = []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            lsb_values.extend([r & 1, g & 1, b & 1])

    one_ratio = sum(lsb_values) / len(lsb_values)
    row_ratios = []
    for y in range(height):
        row_bits = []
        for x in range(width):
            r, g, b = pixels[x, y]
            row_bits.extend([r & 1, g & 1, b & 1])
        row_ratios.append(sum(row_bits) / len(row_bits))

    return {
        "width": width,
        "height": height,
        "capacity_bits": image_capacity_bits(image),
        "lsb_one_ratio": round(one_ratio, 4),
        "row_ratio_stdev": round(statistics.pstdev(row_ratios), 4),
    }


def generate_demo_cover(path: Path, width: int = 256, height: int = 256) -> None:
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    rng = random.Random(42)
    for y in range(height):
        for x in range(width):
            r = (x * 5 + y * 3 + rng.randint(0, 15)) % 256
            g = (x * 2 + y * 7 + rng.randint(0, 15)) % 256
            b = (x * 3 + y * 5 + rng.randint(0, 15)) % 256
            pixels[x, y] = (r, g, b)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def run_demo(output_dir: Path, message: str) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cover_path = output_dir / "sample_cover.png"
    stego_path = output_dir / "sample_stego.png"
    overlay_path = output_dir / "sample_overlay.png"

    generate_demo_cover(cover_path)
    encode_summary = encode_lsb(cover_path, message, stego_path)
    decode_summary = decode_lsb(stego_path)
    compare_summary = compare_images(cover_path, stego_path, overlay_path)
    analysis_summary = analyze_image(stego_path)

    return {
        "cover_path": str(cover_path),
        "stego_path": str(stego_path),
        "overlay_path": str(overlay_path),
        "encode_summary": encode_summary,
        "decode_summary": decode_summary,
        "analysis_summary": analysis_summary,
        "compare_summary": compare_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="LSB steganography encoder, decoder, and baseline comparison utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="Embed a UTF-8 message into a cover image")
    encode_parser.add_argument("--cover", required=True, help="Cover image path")
    encode_parser.add_argument("--message", required=True, help="Message to embed")
    encode_parser.add_argument("--output", required=True, help="Output stego image path")

    decode_parser = subparsers.add_parser("decode", help="Decode a UTF-8 message from an encoded image")
    decode_parser.add_argument("--image", required=True, help="Stego image path")

    compare_parser = subparsers.add_parser("compare", help="Compare a cover image against a suspect image and generate an overlay")
    compare_parser.add_argument("--cover", required=True, help="Original cover image path")
    compare_parser.add_argument("--suspect", required=True, help="Suspect or stego image path")
    compare_parser.add_argument("--output", required=True, help="Overlay image output path")

    analyze_parser = subparsers.add_parser("analyze", help="Summarize LSB distribution in an image")
    analyze_parser.add_argument("--image", required=True, help="Image path")

    demo_parser = subparsers.add_parser("demo", help="Generate a reproducible demo set with cover, stego, and overlay images")
    demo_parser.add_argument("--output-dir", default="samples", help="Directory for generated demo assets")
    demo_parser.add_argument("--message", default="Hidden demo payload for security portfolio validation.", help="Demo message to embed")

    args = parser.parse_args()

    if args.command == "encode":
        summary = encode_lsb(Path(args.cover), args.message, Path(args.output))
        print(json.dumps(summary, indent=2))
        return

    if args.command == "decode":
        print(json.dumps(decode_lsb(Path(args.image)), indent=2))
        return

    if args.command == "compare":
        print(json.dumps(compare_images(Path(args.cover), Path(args.suspect), Path(args.output)), indent=2))
        return

    if args.command == "analyze":
        print(json.dumps(analyze_image(Path(args.image)), indent=2))
        return

    if args.command == "demo":
        print(json.dumps(run_demo(Path(args.output_dir), args.message), indent=2))
        return


if __name__ == "__main__":
    main()
