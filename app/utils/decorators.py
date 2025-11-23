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
            
            # Kiểm tra quyền truy cập
            if user.role.role_name not in allowed_roles:
                # Redirect user về trang dashboard của họ thay vì trả error
                user_role = user.role.role_name
                
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'hotel_owner':
                    return redirect(url_for('owner.dashboard'))
                elif user_role == 'customer':
                    return redirect(url_for('user.dashboard'))
                else:
                    return redirect(url_for('main.index'))
            
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

def room_owner_required(fn):
    """Decorator to check if user owns the room (via hotel ownership) or is admin"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        room_id = kwargs.get('room_id')
        if not room_id:
            return error_response('Room ID required', 400)
        
        from app.models.room import Room
        room = Room.query.get(room_id)
        if not room:
            return error_response('Room not found', 404)
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Check if user is admin or owns the hotel
        if user.role.role_name != 'admin' and room.hotel.owner_id != session['user_id']:
            return error_response('Forbidden', 403)
        
        return fn(*args, **kwargs)
    return wrapper

def booking_owner_or_hotel_owner_required(fn):
    """Decorator to check if user owns the booking or owns the hotel"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        booking_id = kwargs.get('booking_id')
        if not booking_id:
            return error_response('Booking ID required', 400)
        
        from app.models.booking import Booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return error_response('Booking not found', 404)
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Check if user is admin, booking owner, or hotel owner
        is_admin = user.role.role_name == 'admin'
        is_booking_owner = booking.user_id == session['user_id']
        is_hotel_owner = booking.hotel.owner_id == session['user_id']
        
        if not (is_admin or is_booking_owner or is_hotel_owner):
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