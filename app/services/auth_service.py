from app import db
from app.models.user import User
from app.models.role import Role
from datetime import datetime, timedelta
from app.utils.helpers import generate_verification_token, generate_reset_token
from app.models.email_verification import EmailVerification
from app.models.password_reset import PasswordReset

class AuthService:
    
    @staticmethod
    def create_user(email, password, full_name, phone=None):
        customer_role = Role.query.filter_by(role_name='customer').first()
        if not customer_role:
            customer_role = Role(role_name='customer', description='Customer role')
            db.session.add(customer_role)
            db.session.commit()
        
        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            role_id=customer_role.role_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return None, 'Invalid email or password'
        
        if not user.check_password(password):
            return None, 'Invalid email or password'
        
        if not user.is_active:
            return None, 'Account is deactivated'
        
        return user, None
    
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
        verification = EmailVerification.query.filter_by(token=token, is_used=False).first()
        
        if not verification:
            return None, 'Invalid or expired token'
        
        if datetime.utcnow() > verification.expires_at:
            return None, 'Token has expired'
        
        user = User.query.get(verification.user_id)
        if not user:
            return None, 'User not found'
        
        user.email_verified = True
        verification.is_used = True
        
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def create_reset_token(user):
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
        reset = PasswordReset.query.filter_by(token=token, is_used=False).first()
        
        if not reset:
            return None, 'Invalid or expired token'
        
        if datetime.utcnow() > reset.expires_at:
            return None, 'Token has expired'
        
        return reset, None
    
    @staticmethod
    def reset_password(token, new_password):
        reset, error = AuthService.verify_reset_token(token)
        
        if error:
            return None, error
        
        user = User.query.get(reset.user_id)
        if not user:
            return None, 'User not found'
        
        user.set_password(new_password)
        reset.is_used = True
        
        db.session.commit()
        
        return user, None


