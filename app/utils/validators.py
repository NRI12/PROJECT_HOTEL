import re
from app.utils.constants import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH

COMMON_PASSWORDS = [
    'password', '123456', '12345678', 'qwerty', 'abc123', 'password123',
    'admin', 'letmein', 'welcome', 'monkey', '1234567890', 'password1'
]

def is_valid_email(email):
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def normalize_email(email):
    if not email:
        return None
    return email.lower().strip()

def is_valid_phone(phone):
    if not phone:
        return False
    pattern = r'^(\+84|0)[0-9]{9,10}$'
    return re.match(pattern, phone) is not None

def is_valid_password(password):
    if not password:
        return False, 'Mật khẩu là bắt buộc'
    
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f'Mật khẩu phải có ít nhất {PASSWORD_MIN_LENGTH} ký tự'
    
    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f'Mật khẩu không được vượt quá {PASSWORD_MAX_LENGTH} ký tự'
    
    if not re.search(r'[A-Z]', password):
        return False, 'Mật khẩu phải chứa ít nhất một chữ cái viết hoa'
    
    if not re.search(r'[a-z]', password):
        return False, 'Mật khẩu phải chứa ít nhất một chữ cái viết thường'
    
    if not re.search(r'\d', password):
        return False, 'Mật khẩu phải chứa ít nhất một số'
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Mật khẩu phải chứa ít nhất một ký tự đặc biệt (!@#$%^&*(),.?":{}|<>)'
    
    if password.lower() in [p.lower() for p in COMMON_PASSWORDS]:
        return False, 'Mật khẩu quá phổ biến. Vui lòng chọn mật khẩu mạnh hơn'
    
    return True, None

def is_valid_full_name(full_name):
    if not full_name:
        return False, 'Họ tên là bắt buộc'
    
    if len(full_name) < 2:
        return False, 'Họ tên phải có ít nhất 2 ký tự'
    
    if len(full_name) > 100:
        return False, 'Họ tên không được vượt quá 100 ký tự'
    
    pattern = r'^[a-zA-ZÀ-ỹ\s\-\']+$'
    if not re.match(pattern, full_name):
        return False, 'Họ tên chỉ được chứa chữ cái, khoảng trắng, dấu gạch ngang và dấu nháy'
    
    if re.search(r'\s{2,}', full_name):
        return False, 'Họ tên không được chứa nhiều khoảng trắng liên tiếp'
    
    if full_name != full_name.strip():
        return False, 'Họ tên không được có khoảng trắng ở đầu hoặc cuối'
    
    return True, None

def sanitize_input(text):
    if not text:
        return text
    
    dangerous_chars = ['<', '>', '&', '"', "'", '/', '\\']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def is_valid_token_format(token):
    if not token:
        return False
    
    if len(token) < 32 or len(token) > 255:
        return False
    
    pattern = r'^[a-zA-Z0-9\-]+$'
    return re.match(pattern, token) is not None

def validate_required_fields(data, required_fields):
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Thiếu các trường bắt buộc: {', '.join(missing_fields)}"
    return True, None


