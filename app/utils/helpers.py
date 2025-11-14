import secrets
import string
from datetime import datetime, timedelta

def generate_random_token(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_verification_token():
    return generate_random_token(64)

def generate_reset_token():
    return generate_random_token(64)

def is_token_expired(created_at, expiry_hours=24):
    if not created_at:
        return True
    expiry_time = created_at + timedelta(hours=expiry_hours)
    return datetime.utcnow() > expiry_time


