from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.schemas.user_schema import UserRegistrationSchema, UserLoginSchema, ForgotPasswordSchema, ResetPasswordSchema
from app.utils.response import success_response, error_response
from marshmallow import ValidationError

class AuthController:
    
    @staticmethod
    def register():
        try:
            data = request.get_json()
            schema = UserRegistrationSchema()
            validated_data = schema.load(data)
            
            existing_user = User.query.filter_by(email=validated_data['email']).first()
            if existing_user:
                return error_response('Email already registered', 409)
            
            user = AuthService.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                full_name=validated_data['full_name'],
                phone=validated_data.get('phone')
            )
            
            token = AuthService.create_verification_token(user)
            EmailService.send_verification_email(user, token)
            
            access_token = create_access_token(identity=user.user_id)
            refresh_token = create_refresh_token(identity=user.user_id)
            
            return success_response(
                data={
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                },
                message='Registration successful. Please check your email to verify your account.',
                status_code=201
            )
            
        except ValidationError as e:
            return error_response('Validation error', 400, e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Registration failed: {str(e)}', 500)
    
    @staticmethod
    def login():
        try:
            data = request.get_json()
            schema = UserLoginSchema()
            validated_data = schema.load(data)
            
            user, error = AuthService.authenticate_user(
                validated_data['email'],
                validated_data['password']
            )
            
            if error:
                return error_response(error, 401)
            
            access_token = create_access_token(identity=user.user_id)
            refresh_token = create_refresh_token(identity=user.user_id)
            
            return success_response(
                data={
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                },
                message='Login successful'
            )
            
        except ValidationError as e:
            return error_response('Validation error', 400, e.messages)
        except Exception as e:
            return error_response(f'Login failed: {str(e)}', 500)
    
    @staticmethod
    @jwt_required()
    def logout():
        return success_response(message='Logout successful')
    
    @staticmethod
    @jwt_required(refresh=True)
    def refresh():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                return error_response('User not found or inactive', 404)
            
            access_token = create_access_token(identity=user_id)
            
            return success_response(
                data={
                    'access_token': access_token
                },
                message='Token refreshed successfully'
            )
            
        except Exception as e:
            return error_response(f'Token refresh failed: {str(e)}', 500)
    
    @staticmethod
    def forgot_password():
        try:
            data = request.get_json()
            schema = ForgotPasswordSchema()
            validated_data = schema.load(data)
            
            user = User.query.filter_by(email=validated_data['email']).first()
            
            if user:
                token = AuthService.create_reset_token(user)
                EmailService.send_reset_password_email(user, token)
            
            return success_response(
                message='If the email exists, a password reset link has been sent.'
            )
            
        except ValidationError as e:
            return error_response('Validation error', 400, e.messages)
        except Exception as e:
            return error_response(f'Request failed: {str(e)}', 500)
    
    @staticmethod
    def reset_password():
        try:
            data = request.get_json()
            schema = ResetPasswordSchema()
            validated_data = schema.load(data)
            
            user, error = AuthService.reset_password(
                validated_data['token'],
                validated_data['new_password']
            )
            
            if error:
                return error_response(error, 400)
            
            return success_response(message='Password reset successful')
            
        except ValidationError as e:
            return error_response('Validation error', 400, e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Password reset failed: {str(e)}', 500)
    
    @staticmethod
    def verify_email():
        try:
            data = request.get_json()
            token = data.get('token')
            
            if not token:
                return error_response('Token is required', 400)
            
            user, error = AuthService.verify_email_token(token)
            
            if error:
                return error_response(error, 400)
            
            return success_response(
                data={'user': user.to_dict()},
                message='Email verified successfully'
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Email verification failed: {str(e)}', 500)
    
    @staticmethod
    @jwt_required()
    def resend_verification():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return error_response('User not found', 404)
            
            if user.email_verified:
                return error_response('Email already verified', 400)
            
            token = AuthService.create_verification_token(user)
            EmailService.send_verification_email(user, token)
            
            return success_response(message='Verification email sent successfully')
            
        except Exception as e:
            return error_response(f'Failed to resend verification email: {str(e)}', 500)


