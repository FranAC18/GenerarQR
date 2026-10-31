"""Authenticated application-level encryption for selected database fields."""

import base64
import hashlib
import hmac
import os
from functools import lru_cache
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ENCRYPTED_PREFIX = "enc:v1:"
NONCE_SIZE = 12


@lru_cache(maxsize=1)
def _master_key() -> bytes:
    """Load a 256-bit key encoded as URL-safe Base64 from the server environment."""
    encoded = os.getenv("FIELD_ENCRYPTION_KEY", "").strip()
    if not encoded:
        raise RuntimeError("Falta configurar FIELD_ENCRYPTION_KEY en el entorno del servidor.")

    try:
        key = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
    except Exception as exc:
        raise RuntimeError("FIELD_ENCRYPTION_KEY debe estar codificada en Base64 URL-safe.") from exc

    if len(key) != 32:
        raise RuntimeError("FIELD_ENCRYPTION_KEY debe representar exactamente 32 bytes (256 bits).")
    return key


def encryption_ready() -> bool:
    """Return whether a valid server-side encryption key is configured."""
    try:
        _master_key()
        return True
    except RuntimeError:
        return False


def encrypt_text(value: Optional[str], field_name: str) -> Optional[str]:
    """Encrypt a string with AES-256-GCM and bind it to its table/column name."""
    if value is None:
        return None

    text = str(value)
    nonce = os.urandom(NONCE_SIZE)
    aad = f"kobaia:{field_name}:v1".encode("utf-8")
    encrypted = AESGCM(_master_key()).encrypt(nonce, text.encode("utf-8"), aad)
    payload = base64.urlsafe_b64encode(nonce + encrypted).decode("ascii").rstrip("=")
    return f"{ENCRYPTED_PREFIX}{payload}"


def decrypt_text(value: Optional[str], field_name: str) -> Optional[str]:
    """Decrypt an encrypted value; pass legacy plaintext values through unchanged."""
    if value is None:
        return None
    if not value.startswith(ENCRYPTED_PREFIX):
        return value

    encoded = value[len(ENCRYPTED_PREFIX):]
    try:
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        if len(payload) <= NONCE_SIZE:
            raise ValueError("contenido cifrado incompleto")
        nonce, ciphertext = payload[:NONCE_SIZE], payload[NONCE_SIZE:]
        aad = f"kobaia:{field_name}:v1".encode("utf-8")
        plaintext = AESGCM(_master_key()).decrypt(nonce, ciphertext, aad)
        return plaintext.decode("utf-8")
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo descifrar {field_name}; revise la clave y la integridad del dato."
        ) from exc


def blind_index(value: str, purpose: str) -> str:
    """Create a keyed, non-reversible HMAC digest for a username."""
    key = hmac.new(_master_key(), b"kobaia:blind-index:v1", hashlib.sha256).digest()
    normalized = value.strip().casefold().encode("utf-8")
    return hmac.new(key, purpose.encode("utf-8") + b":" + normalized, hashlib.sha256).hexdigest()
