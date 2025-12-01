import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/hotel_booking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Session cookie settings để giữ session qua PayPal redirect
    SESSION_COOKIE_SAMESITE = 'Lax'  # Cho phép cookie qua redirect
    SESSION_COOKIE_SECURE = False    # True nếu dùng HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_NAME = 'session'  # Tên cookie session
    # Không set SESSION_COOKIE_DOMAIN để cookie hoạt động với localhost
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')
    
    FRONTEND_URL = os.environ.get('FRONTEND_URL')
    
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID') or os.environ.get('PAYPAL-SANDBOX-CLIENT-ID')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE') or os.environ.get('PAYPAL_ENVIRONMENT', 'sandbox')
    PAYPAL_RETURN_URL = os.environ.get('PAYPAL_RETURN_URL') or 'http://localhost:5000/payment/paypal-return'
    PAYPAL_CANCEL_URL = os.environ.get('PAYPAL_CANCEL_URL') or 'http://localhost:5000/payment/paypal-cancel'
config = {
    'development': Config,
    'production': Config,
    'default': Config
}


