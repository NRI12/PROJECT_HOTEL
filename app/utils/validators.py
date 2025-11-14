import re
from app.utils.constants import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    pattern = r'^(\+84|0)[0-9]{9,10}$'
    return re.match(pattern, phone) is not None

def is_valid_password(password):
    if not password or len(password) < PASSWORD_MIN_LENGTH:
        return False, f'Password must be at least {PASSWORD_MIN_LENGTH} characters'
    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f'Password must not exceed {PASSWORD_MAX_LENGTH} characters'
    return True, None

def validate_required_fields(data, required_fields):
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None


