from flask import request, session
from app import db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.schemas.user_schema import UserRegistrationSchema, UserLoginSchema, ForgotPasswordSchema, ResetPasswordSchema
from app.utils.response import success_response, error_response, validation_error_response
from app.utils.validators import validate_required_fields, is_valid_token_format
from marshmallow import ValidationError

class AuthController:
    
    @staticmethod
    def _get_request_data():
        if request.form:
            data = dict(request.form)
            for key, value in data.items():
                if isinstance(value, list) and len(value) == 1:
                    data[key] = value[0]
            return data
        elif request.is_json:
            return request.get_json() or {}
        else:
            return {}
    
    @staticmethod
    def register():
        try:
            data = AuthController._get_request_data()
            if not data:
                return error_response('Yêu cầu phải có dữ liệu', 400)
            
            required_fields = ['email', 'password', 'full_name']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = UserRegistrationSchema()
            validated_data = schema.load(data)
            
            existing_user = User.query.filter_by(email=validated_data['email']).first()
            if existing_user:
                return error_response('Email đã được đăng ký', 409)
            
            user = AuthService.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                full_name=validated_data['full_name'],
                phone=validated_data.get('phone')
            )
            
            token = AuthService.create_verification_token(user)
            EmailService.send_verification_email(user, token)
            
            return success_response(
                data={'user': user.to_dict()},
                message='Đăng ký thành công. Vui lòng kiểm tra email để xác thực tài khoản.',
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Đăng ký thất bại: {str(e)}', 500)
    
    @staticmethod
    def login():
        try:
            data = AuthController._get_request_data()
            if not data:
                return error_response('Yêu cầu phải có dữ liệu', 400)
            
            required_fields = ['email', 'password']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = UserLoginSchema()
            validated_data = schema.load(data)
            
            user, error = AuthService.authenticate_user(
                validated_data['email'],
                validated_data['password'],
                request.remote_addr,
                request.headers.get('User-Agent')
            )
            
            if error:
                return error_response(error, 401)
            
            if not user.email_verified:
                return error_response(
                    'Vui lòng xác thực email trước khi đăng nhập. Kiểm tra hộp thư của bạn để tìm liên kết xác thực.',
                    403
                )
            
            session['user_id'] = user.user_id
            session.permanent = True
            
            return success_response(
                data={'user': user.to_dict()},
                message='Đăng nhập thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            return error_response(f'Đăng nhập thất bại: {str(e)}', 500)
    
    @staticmethod
    def logout():
        session.clear()
        return success_response(message='Đăng xuất thành công')
    
    @staticmethod
    def verify_token():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            return error_response('Token không hợp lệ hoặc tài khoản không hoạt động', 401)
        
        return success_response(
            data={'user': user.to_dict()},
            message='Token hợp lệ'
        )
    
    @staticmethod
    def forgot_password():
        try:
            data = AuthController._get_request_data()
            if not data:
                return error_response('Yêu cầu phải có dữ liệu', 400)
            
            required_fields = ['email']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = ForgotPasswordSchema()
            validated_data = schema.load(data)
            
            user = User.query.filter_by(email=validated_data['email']).first()
            
            if user:
                token = AuthService.create_reset_token(user)
                EmailService.send_reset_password_email(user, token)
            
            return success_response(
                message='Nếu email tồn tại, liên kết đặt lại mật khẩu đã được gửi.'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            return error_response(f'Yêu cầu thất bại: {str(e)}', 500)
    
    @staticmethod
    def reset_password():
        try:
            data = AuthController._get_request_data()
            if not data:
                return error_response('Yêu cầu phải có dữ liệu', 400)
            
            required_fields = ['token', 'new_password']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            if 'token' in data and not is_valid_token_format(data['token']):
                return error_response('Định dạng token không hợp lệ', 400)
            
            schema = ResetPasswordSchema()
            validated_data = schema.load(data)
            
            user, error = AuthService.reset_password(
                validated_data['token'],
                validated_data['new_password']
            )
            
            if error:
                return error_response(error, 400)
            
            return success_response(message='Đặt lại mật khẩu thành công')
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Đặt lại mật khẩu thất bại: {str(e)}', 500)
    
    @staticmethod
    def verify_email():
        try:
            data = AuthController._get_request_data()
            if not data:
                return error_response('Yêu cầu phải có dữ liệu', 400)
            
            required_fields = ['token']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            token = data.get('token')
            
            if not is_valid_token_format(token):
                return error_response('Định dạng token không hợp lệ', 400)
            
            user, error = AuthService.verify_email_token(token)
            
            if error:
                return error_response(error, 400)
            
            return success_response(
                data={'user': user.to_dict()},
                message='Xác thực email thành công'
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xác thực email thất bại: {str(e)}', 500)
    
    @staticmethod
    def resend_verification():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        
        if not user:
            return error_response('Không tìm thấy người dùng', 404)
        
        if user.email_verified:
            return error_response('Email đã được xác thực', 400)
        
        token = AuthService.create_verification_token(user)
        EmailService.send_verification_email(user, token)
        
        return success_response(message='Email xác thực đã được gửi thành công')