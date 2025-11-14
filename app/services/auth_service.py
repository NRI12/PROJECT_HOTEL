from app import db
from app.models.user import User
from app.models.role import Role
from app.models.login_history import LoginHistory
from datetime import datetime, timedelta
from app.utils.helpers import generate_verification_token, generate_reset_token
from app.utils.validators import normalize_email
from app.models.email_verification import EmailVerification
from app.models.password_reset import PasswordReset

class AuthService:
    
    @staticmethod
    def create_user(email, password, full_name, phone=None):
        email = normalize_email(email) if email else None
        
        if not email:
            raise ValueError('Email là bắt buộc')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError('Email đã được đăng ký')
        
        customer_role = Role.query.filter_by(role_name='customer').first()
        if not customer_role:
            customer_role = Role(role_name='customer', description='Customer role')
            db.session.add(customer_role)
            db.session.commit()
        
        user = User(
            email=email,
            full_name=full_name.strip() if full_name else None,
            phone=phone.strip() if phone else None,
            role_id=customer_role.role_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate_user(email, password, ip_address=None, user_agent=None):
        email = normalize_email(email) if email else None
        
        if not email:
            return None, 'Email là bắt buộc'
        
        if not password:
            return None, 'Mật khẩu là bắt buộc'
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return None, 'Email hoặc mật khẩu không đúng'
        
        if not user.is_active:
            return None, 'Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ hỗ trợ.'
        
        if not user.check_password(password):
            AuthService._log_failed_login(user.user_id, ip_address, user_agent)
            return None, 'Email hoặc mật khẩu không đúng'
        
        AuthService._log_successful_login(user.user_id, ip_address, user_agent)
        
        return user, None
    
    @staticmethod
    def _log_successful_login(user_id, ip_address=None, user_agent=None):
        try:
            login_history = LoginHistory(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                login_at=datetime.utcnow()
            )
            db.session.add(login_history)
            db.session.commit()
        except Exception:
            db.session.rollback()
    
    @staticmethod
    def _log_failed_login(user_id, ip_address=None, user_agent=None):
        try:
            pass
        except Exception:
            pass
    
    @staticmethod
    def create_verification_token(user):
        token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        verification = EmailVerification(
            user_id=user.user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(verification)
        db.session.commit()
        
        return token
    
    @staticmethod
    def verify_email_token(token):
        if not token:
            return None, 'Token là bắt buộc'
        
        verification = EmailVerification.query.filter_by(token=token, is_used=False).first()
        
        if not verification:
            return None, 'Token không hợp lệ hoặc đã hết hạn'
        
        if datetime.utcnow() > verification.expires_at:
            return None, 'Token đã hết hạn. Vui lòng yêu cầu email xác thực mới.'
        
        user = User.query.get(verification.user_id)
        if not user:
            return None, 'Không tìm thấy người dùng'
        
        if not user.is_active:
            return None, 'Tài khoản đã bị vô hiệu hóa'
        
        if user.email_verified:
            return None, 'Email đã được xác thực'
        
        user.email_verified = True
        verification.is_used = True
        
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def create_reset_token(user):
        if not user:
            raise ValueError('Người dùng là bắt buộc')
        
        if not user.is_active:
            raise ValueError('Không thể đặt lại mật khẩu cho tài khoản đã bị vô hiệu hóa')
        
        existing_resets = PasswordReset.query.filter_by(
            user_id=user.user_id,
            is_used=False
        ).all()
        
        for reset in existing_resets:
            reset.is_used = True
        
        token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        reset = PasswordReset(
            user_id=user.user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset)
        db.session.commit()
        
        return token
    
    @staticmethod
    def verify_reset_token(token):
        if not token:
            return None, 'Token là bắt buộc'
        
        reset = PasswordReset.query.filter_by(token=token, is_used=False).first()
        
        if not reset:
            return None, 'Token không hợp lệ hoặc đã hết hạn'
        
        if datetime.utcnow() > reset.expires_at:
            return None, 'Token đã hết hạn. Vui lòng yêu cầu liên kết đặt lại mật khẩu mới.'
        
        user = User.query.get(reset.user_id)
        if not user:
            return None, 'Không tìm thấy người dùng'
        
        if not user.is_active:
            return None, 'Tài khoản đã bị vô hiệu hóa'
        
        return reset, None
    
    @staticmethod
    def reset_password(token, new_password):
        if not token:
            return None, 'Token là bắt buộc'
        
        if not new_password:
            return None, 'Mật khẩu mới là bắt buộc'
        
        reset, error = AuthService.verify_reset_token(token)
        
        if error:
            return None, error
        
        user = User.query.get(reset.user_id)
        if not user:
            return None, 'Không tìm thấy người dùng'
        
        if not user.is_active:
            return None, 'Tài khoản đã bị vô hiệu hóa'
        
        if user.check_password(new_password):
            return None, 'Mật khẩu mới phải khác với mật khẩu hiện tại'
        
        user.set_password(new_password)
        reset.is_used = True
        
        db.session.commit()
        
        return user, None


