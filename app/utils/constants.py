USER_ROLES = {
    'ADMIN': 'admin',
    'HOTEL_OWNER': 'hotel_owner',
    'CUSTOMER': 'customer'
}

NOTIFICATION_TYPES = {
    'BOOKING': 'booking',
    'PAYMENT': 'payment',
    'PROMOTION': 'promotion',
    'SYSTEM': 'system',
    'REVIEW': 'review'
}

JWT_TOKEN_LOCATION = ['headers']
JWT_HEADER_NAME = 'Authorization'
JWT_HEADER_TYPE = 'Bearer'

PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 128

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


