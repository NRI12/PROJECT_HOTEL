from marshmallow import Schema, fields, validate, validates, ValidationError
from app.utils.validators import is_valid_email, is_valid_phone, is_valid_password

class UserRegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.Str(allow_none=True)
    
    @validates('email')
    def validate_email(self, value):
        if not is_valid_email(value):
            raise ValidationError('Invalid email format')
    
    @validates('phone')
    def validate_phone(self, value):
        if value and not is_valid_phone(value):
            raise ValidationError('Invalid phone format')
    
    @validates('password')
    def validate_password(self, value):
        is_valid, message = is_valid_password(value)
        if not is_valid:
            raise ValidationError(message)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserUpdateSchema(Schema):
    full_name = fields.Str(validate=validate.Length(min=2, max=100))
    phone = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    id_card = fields.Str(allow_none=True, validate=validate.Length(max=50))
    
    @validates('phone')
    def validate_phone(self, value):
        if value and not is_valid_phone(value):
            raise ValidationError('Invalid phone format')

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    
    @validates('new_password')
    def validate_password(self, value):
        is_valid, message = is_valid_password(value)
        if not is_valid:
            raise ValidationError(message)

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    
    @validates('new_password')
    def validate_password(self, value):
        is_valid, message = is_valid_password(value)
        if not is_valid:
            raise ValidationError(message)


