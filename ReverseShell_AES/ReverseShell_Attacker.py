from __future__ import annotations

import argparse
import json
import socket
from datetime import datetime, timezone

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hashlib import sha256


KEY = sha256(b"safe_remote_lab_key").digest()
NONCE_SIZE = 12

SAFE_TASKS = {
    "collect_hostname": {"task_type": "collect_hostname", "description": "Return the client hostname"},
    "collect_os": {"task_type": "collect_os", "description": "Return operating system metadata"},
    "collect_time": {"task_type": "collect_time", "description": "Return the client's current UTC timestamp"},
    "heartbeat": {"task_type": "heartbeat", "description": "Return a liveness message"},
}


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


def run_server(host: str, port: int, task_name: str) -> None:
    if task_name not in SAFE_TASKS:
        raise ValueError(f"Unsupported task: {task_name}")

    task = {
        "task_id": f"task-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "issued_at": datetime.now(timezone.utc).isoformat(),
        **SAFE_TASKS[task_name],
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        print(f"Encrypted task server listening on {host}:{port}")
        conn, addr = server.accept()
        with conn:
            print(f"Client connected from {addr[0]}:{addr[1]}")
            conn.sendall(encrypt_message(task))
            response = decrypt_message(conn)
            print(json.dumps(response, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Safe AES-encrypted remote task server for local lab simulation")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4444)
    parser.add_argument("--task", choices=sorted(SAFE_TASKS.keys()), default="heartbeat")
    args = parser.parse_args()
    run_server(args.host, args.port, args.task)


if __name__ == "__main__":
    main()
