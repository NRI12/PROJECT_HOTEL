from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load
from app.utils.validators import (
    is_valid_email, is_valid_phone, is_valid_password, 
    normalize_email, is_valid_full_name, is_valid_token_format
)

class UserRegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.Str(allow_none=True)
    
    @pre_load
    def normalize_data(self, data, **kwargs):
        if 'email' in data and data['email']:
            data['email'] = normalize_email(data['email'])
        if 'full_name' in data and data['full_name']:
            data['full_name'] = data['full_name'].strip()
        if 'phone' in data and data['phone']:
            data['phone'] = data['phone'].strip()
        return data
    
    @validates('email')
    def validate_email(self, value, **kwargs):
        if not value:
            raise ValidationError('Email là bắt buộc')
        if not is_valid_email(value):
            raise ValidationError('Định dạng email không hợp lệ')
        if len(value) > 100:
            raise ValidationError('Email quá dài (tối đa 100 ký tự)')
    
    @validates('full_name')
    def validate_full_name(self, value, **kwargs):
        is_valid, message = is_valid_full_name(value)
        if not is_valid:
            raise ValidationError(message)
    
    @validates('phone')
    def validate_phone(self, value, **kwargs):
        if value and not is_valid_phone(value):
            raise ValidationError('Định dạng số điện thoại không hợp lệ. Sử dụng định dạng Việt Nam: +84xxxxxxxxx hoặc 0xxxxxxxxx')
    
    @validates('password')
    def validate_password(self, value, **kwargs):
        if not value:
            raise ValidationError('Mật khẩu là bắt buộc')
        is_valid, message = is_valid_password(value)
        if not is_valid:
            raise ValidationError(message)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))
    
    @pre_load
    def normalize_data(self, data, **kwargs):
        if 'email' in data and data['email']:
            data['email'] = normalize_email(data['email'])
        return data
    
    @validates('email')
    def validate_email(self, value, **kwargs):
        if not value:
            raise ValidationError('Email là bắt buộc')
        if not is_valid_email(value):
            raise ValidationError('Định dạng email không hợp lệ')
    
    @validates('password')
    def validate_password(self, value, **kwargs):
        if not value:
            raise ValidationError('Mật khẩu là bắt buộc')
        if len(value) < 1:
            raise ValidationError('Mật khẩu không được để trống')

class UserUpdateSchema(Schema):
    full_name = fields.Str(validate=validate.Length(min=2, max=100))
    phone = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True, validate=validate.Length(max=500))
    id_card = fields.Str(allow_none=True, validate=validate.Length(max=50))
    
    @pre_load
    def normalize_data(self, data, **kwargs):
        if 'full_name' in data and data['full_name']:
            data['full_name'] = data['full_name'].strip()
        if 'phone' in data and data['phone']:
            data['phone'] = data['phone'].strip()
        if 'address' in data and data['address']:
            data['address'] = data['address'].strip()
        if 'id_card' in data and data['id_card']:
            data['id_card'] = data['id_card'].strip()
        return data
    
    @validates('full_name')
    def validate_full_name(self, value, **kwargs):
        if value:
            is_valid, message = is_valid_full_name(value)
            if not is_valid:
                raise ValidationError(message)
    
    @validates('phone')
    def validate_phone(self, value, **kwargs):
        if value and not is_valid_phone(value):
            raise ValidationError('Định dạng số điện thoại không hợp lệ. Sử dụng định dạng Việt Nam: +84xxxxxxxxx hoặc 0xxxxxxxxx')

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    
    @validates('old_password')
    def validate_old_password(self, value, **kwargs):
        if not value:
            raise ValidationError('Mật khẩu cũ là bắt buộc')
    
    @validates('new_password')
    def validate_password(self, value, **kwargs):
        if not value:
            raise ValidationError('Mật khẩu mới là bắt buộc')
        is_valid, message = is_valid_password(value)
        if not is_valid:
            raise ValidationError(message)

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)
    
    @pre_load
    def normalize_data(self, data, **kwargs):
        if 'email' in data and data['email']:
            data['email'] = normalize_email(data['email'])
        return data
    
    @validates('email')
    def validate_email(self, value, **kwargs):
        if not value:
            raise ValidationError('Email là bắt buộc')
        if not is_valid_email(value):
            raise ValidationError('Định dạng email không hợp lệ')

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    
    @validates('token')
    def validate_token(self, value, **kwargs):
        if not value:
            raise ValidationError('Token là bắt buộc')
        if not is_valid_token_format(value):
            raise ValidationError('Định dạng token không hợp lệ')
    
    @validates('new_password')
    def validate_password(self, value, **kwargs):
        if not value:
            raise ValidationError('Mật khẩu mới là bắt buộc')
        is_valid, message = is_valid_password(value)
        if not is_valid:
            raise ValidationError(message)


