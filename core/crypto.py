import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from core.config import settings

def encrypt_telemetry(payload: bytes) -> bytes:
    """Encrypts telemetry payload using AES-256-GCM."""
    aesgcm = AESGCM(settings.TELEMETRY_AES_KEY)
    nonce = os.urandom(12) # GCM standard nonce size is 12 bytes
    ciphertext = aesgcm.encrypt(nonce, payload, None)
    # Prepend nonce to the ciphertext for decryption
    return nonce + ciphertext

def decrypt_telemetry(encrypted_payload: bytes) -> bytes:
    """Decrypts telemetry payload using AES-256-GCM."""
    aesgcm = AESGCM(settings.TELEMETRY_AES_KEY)
    nonce = encrypted_payload[:12]
    ciphertext = encrypted_payload[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)
