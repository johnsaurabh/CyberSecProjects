from __future__ import annotations

import argparse
import json
import platform
import socket
from datetime import datetime, timezone

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hashlib import sha256


KEY = sha256(b"safe_remote_lab_key").digest()
NONCE_SIZE = 12


def encrypt_message(payload: dict) -> bytes:
    nonce = get_random_bytes(NONCE_SIZE)
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
    plaintext = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    envelope = {
        "nonce": nonce.hex(),
        "tag": tag.hex(),
        "ciphertext": ciphertext.hex(),
    }
    encoded = json.dumps(envelope).encode("utf-8")
    return len(encoded).to_bytes(4, "big") + encoded


def decrypt_message(sock: socket.socket) -> dict:
    header = recv_exact(sock, 4)
    size = int.from_bytes(header, "big")
    envelope = json.loads(recv_exact(sock, size).decode("utf-8"))
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=bytes.fromhex(envelope["nonce"]))
    plaintext = cipher.decrypt_and_verify(bytes.fromhex(envelope["ciphertext"]), bytes.fromhex(envelope["tag"]))
    return json.loads(plaintext.decode("utf-8"))


def recv_exact(sock: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Socket closed during framed read")
        data.extend(chunk)
    return bytes(data)


def execute_safe_task(task: dict) -> dict:
    task_type = task["task_type"]
    if task_type == "collect_hostname":
        return {"hostname": socket.gethostname()}
    if task_type == "collect_os":
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
        }
    if task_type == "collect_time":
        return {"utc_time": datetime.now(timezone.utc).isoformat()}
    if task_type == "heartbeat":
        return {"message": "client alive"}
    return {"error": f"Unsupported task type: {task_type}"}


def run_client(server_host: str, server_port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((server_host, server_port))
        task = decrypt_message(client)
        result = {
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "result": execute_safe_task(task),
        }
        client.sendall(encrypt_message(result))
        print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Safe AES-encrypted remote task client for local lab simulation")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4444)
    args = parser.parse_args()
    run_client(args.host, args.port)


if __name__ == "__main__":
    main()
