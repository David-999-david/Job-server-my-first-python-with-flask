import secrets
import hmac
import hashlib
from flask import current_app
from datetime import datetime, timezone


def generate_random(n=6) -> str:
    return f'{secrets.randbelow(10**n):0{n}d}'


def pepper() -> bytes:
    secret = current_app.config.get('OTP_HMAC_SECRET')
    if not secret:
        raise RuntimeError('otp hmac is not set')
    return secret.encode('utf-8')


def hash_code(code: str) -> str:
    return hmac.new(pepper(), code.encode('utf-8'), hashlib.sha256).hexdigest()


def compare_otp(intput_code: str, store_otp: str) -> bool:
    hashed = hash_code(intput_code)
    return hmac.compare_digest(hashed, store_otp)


def utcnow():
    return datetime.now(timezone.utc)
