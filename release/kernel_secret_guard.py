from __future__ import annotations
import hashlib

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def redact_secret(text: str, secret: str | None) -> tuple[str, bool]:
    if not secret or len(secret) < 8:
        return text, False
    if secret not in text:
        return text, False
    digest = sha256_text(secret)[:12]
    return text.replace(secret, f"[REDACTED_SHA256_{digest}]"), True
