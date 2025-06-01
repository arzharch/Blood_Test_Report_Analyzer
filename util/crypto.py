# utils/crypto.py

import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

# Load 32-byte key from environment (base64-encoded)
RAW_KEY = os.getenv("ENCRYPTION_KEY")
if RAW_KEY is None:
    raise ValueError("ENCRYPTION_KEY is not set in the environment")

# Decode into 32-byte key
try:
    KEY = base64.urlsafe_b64decode(RAW_KEY)
except Exception as e:
    raise ValueError("Failed to decode ENCRYPTION_KEY. Must be base64-encoded 32-byte key.") from e

def encrypt_file(file_bytes: bytes) -> str:
    aesgcm = AESGCM(KEY)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, file_bytes, None)
    return base64.b64encode(nonce + encrypted).decode("utf-8")

def decrypt_file(encrypted_data: str) -> bytes:
    try:
        data = base64.b64decode(encrypted_data)
        nonce, ciphertext = data[:12], data[12:]
        aesgcm = AESGCM(KEY)
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError("Decryption failed.") from e
