from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _get_fernet():
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", "")
    if not key:
        raise ValueError("FIELD_ENCRYPTION_KEY is not configured in settings/environment.")
    return Fernet(key.encode("utf-8") if isinstance(key, str) else key)


def encrypt_text(plain_text: str) -> str:
    if not plain_text:
        return ""
    token = _get_fernet().encrypt(plain_text.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_text(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    try:
        plain = _get_fernet().decrypt(cipher_text.encode("utf-8"))
        return plain.decode("utf-8")
    except InvalidToken:
        return "[Unable to decrypt: invalid key or corrupted ciphertext]"