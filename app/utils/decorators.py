from functools import wraps
from flask import session, redirect, url_for, request
from app.models.user import User
from app.models.hotel import Hotel
from app.utils.response import error_response
from app.utils.constants import USER_ROLES

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return wrapper

def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            user = User.query.get(session['user_id'])
            if not user or not user.is_active:
                session.clear()
                return redirect(url_for('auth.login'))
            
            if user.role.role_name not in allowed_roles:
                return error_response('Insufficient permissions', 403)
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def hotel_owner_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        hotel_id = kwargs.get('hotel_id')
        if not hotel_id:
            return error_response('Hotel ID required', 400)
        
        hotel = Hotel.query.get(hotel_id)
        if not hotel:
            return error_response('Hotel not found', 404)
        
        user = User.query.get(session['user_id'])
        if hotel.owner_id != session['user_id'] and user.role.role_name != 'admin':
            return error_response('Forbidden', 403)
        
        return fn(*args, **kwargs)
    return wrapper

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