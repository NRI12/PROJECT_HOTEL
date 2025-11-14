from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
from app.utils.response import error_response
from app.utils.constants import USER_ROLES

def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return error_response('User not found', 404)
            
            if not user.is_active:
                return error_response('Account is deactivated', 403)
            
            if user.role.role_name not in allowed_roles:
                return error_response('Insufficient permissions', 403)
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def validate_json(*required_fields):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return error_response('Content-Type must be application/json', 400)
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return error_response(
                    f"Missing required fields: {', '.join(missing_fields)}", 
                    400
                )
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


