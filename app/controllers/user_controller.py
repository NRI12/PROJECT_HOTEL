from flask import request, session, redirect, url_for
from app import db
from app.models.user import User
from app.models.notification import Notification
from app.models.favorite import Favorite
from app.schemas.user_schema import UserUpdateSchema, ChangePasswordSchema
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
import os

class UserController:
    
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
    def get_profile():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))
        
        return success_response(data={'user': user.to_dict()})
    
    @staticmethod
    def update_profile():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            user = User.query.get(session['user_id'])
            
            if not user:
                return error_response('User not found', 404)
            
            data = UserController._get_request_data()
            schema = UserUpdateSchema()
            validated_data = schema.load(data)
            
            if 'full_name' in validated_data:
                user.full_name = validated_data['full_name']
            if 'phone' in validated_data:
                user.phone = validated_data['phone']
            if 'address' in validated_data:
                user.address = validated_data['address']
            if 'id_card' in validated_data:
                user.id_card = validated_data['id_card']
            
            db.session.commit()
            
            return success_response(
                data={'user': user.to_dict()},
                message='Cập nhật profile thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật profile thất bại: {str(e)}', 500)
    
    @staticmethod
    def change_password():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            user = User.query.get(session['user_id'])
            
            if not user:
                return error_response('User not found', 404)
            
            data = UserController._get_request_data()
            schema = ChangePasswordSchema()
            validated_data = schema.load(data)
            
            if not user.check_password(validated_data['old_password']):
                return error_response('Mật khẩu hiện tại không đúng', 400)
            
            user.set_password(validated_data['new_password'])
            db.session.commit()
            
            return success_response(message='Đổi mật khẩu thành công')
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Đổi mật khẩu thất bại: {str(e)}', 500)
    
    @staticmethod
    def upload_avatar():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            user = User.query.get(session['user_id'])
            
            if not user:
                return error_response('User not found', 404)
            
            if 'avatar' not in request.files:
                return error_response('Không có file được chọn', 400)
            
            file = request.files['avatar']
            
            if file.filename == '':
                return error_response('Không có file được chọn', 400)
            
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
            if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                return error_response('Định dạng file không hợp lệ. Chỉ chấp nhận: jpg, jpeg, png, gif, webp', 400)
            
            filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
            upload_folder = os.path.join('uploads', 'users')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            user.avatar_url = f"/uploads/users/{filename}"
            db.session.commit()
            
            return success_response(
                data={'avatar_url': user.avatar_url},
                message='Tải lên avatar thành công'
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tải lên avatar thất bại: {str(e)}', 500)
    
    @staticmethod
    def get_bookings():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            user = User.query.get(session['user_id'])
            
            if not user:
                return error_response('User not found', 404)
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            bookings_query = user.bookings
            total = len(bookings_query)
            
            start = (page - 1) * per_page
            end = start + per_page
            
            bookings = []
            for booking in bookings_query[start:end]:
                booking_dict = booking.to_dict()
                booking_dict['hotel'] = booking.hotel.to_dict() if booking.hotel else None
                bookings.append(booking_dict)
            
            return paginated_response(bookings, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Failed to get bookings: {str(e)}', 500)
    
    @staticmethod
    def get_favorites():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            favorites_query = Favorite.query.filter_by(user_id=session['user_id'])
            total = favorites_query.count()
            
            favorites = favorites_query.offset((page - 1) * per_page).limit(per_page).all()
            favorites_data = [favorite.to_dict() for favorite in favorites]
            
            return paginated_response(favorites_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Failed to get favorites: {str(e)}', 500)
    
    @staticmethod
    def get_notifications():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            notifications_query = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc())
            total = notifications_query.count()
            
            notifications = notifications_query.offset((page - 1) * per_page).limit(per_page).all()
            notifications_data = [notif.to_dict() for notif in notifications]
            
            return paginated_response(notifications_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Failed to get notifications: {str(e)}', 500)
    
    @staticmethod
    def mark_notification_read(notification_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            notification = Notification.query.filter_by(
                notification_id=notification_id,
                user_id=session['user_id']
            ).first()
            
            if not notification:
                return error_response('Notification not found', 404)
            
            notification.is_read = True
            db.session.commit()
            
            return success_response(message='Notification marked as read')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Failed to mark notification as read: {str(e)}', 500)
    
    @staticmethod
    def delete_notification(notification_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            notification = Notification.query.filter_by(
                notification_id=notification_id,
                user_id=session['user_id']
            ).first()
            
            if not notification:
                return error_response('Notification not found', 404)
            
            db.session.delete(notification)
            db.session.commit()
            
            return success_response(message='Notification deleted successfully')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Failed to delete notification: {str(e)}', 500)