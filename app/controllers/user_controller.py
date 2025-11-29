from flask import request, session, redirect, url_for
from app import db
from app.models.user import User
from app.models.notification import Notification
from app.models.favorite import Favorite
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.review import Review
from app.models.hotel_image import HotelImage
from app.schemas.user_schema import UserUpdateSchema, ChangePasswordSchema
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from sqlalchemy import func
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
            from datetime import datetime
            from app.models.booking import Booking
            
            user = User.query.get(session['user_id'])
            
            if not user:
                return error_response('User not found', 404)
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            status = request.args.get('status', '').strip()
            start_date = request.args.get('start_date', '').strip()
            end_date = request.args.get('end_date', '').strip()
            
            # Bắt đầu với query từ user.bookings
            bookings_query = Booking.query.filter_by(user_id=user.user_id)
            
            # Filter theo status
            if status:
                bookings_query = bookings_query.filter_by(status=status)
            
            # Filter theo ngày
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    bookings_query = bookings_query.filter(Booking.check_in_date >= start_dt)
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    bookings_query = bookings_query.filter(Booking.check_out_date <= end_dt)
                except ValueError:
                    pass
            
            # Sắp xếp theo ngày tạo mới nhất
            bookings_query = bookings_query.order_by(Booking.created_at.desc())
            
            total = bookings_query.count()
            
            # Phân trang
            bookings_list = bookings_query.offset((page - 1) * per_page).limit(per_page).all()
            
            from app.models.review import Review
            bookings = []
            for booking in bookings_list:
                booking_dict = booking.to_dict()
                booking_dict['hotel'] = booking.hotel.to_dict() if booking.hotel else None
                # Kiểm tra xem booking đã checkout và chưa có review chưa
                booking_dict['can_review'] = False
                booking_dict['has_review'] = False
                if booking.status == 'checked_out':
                    existing_review = Review.query.filter_by(booking_id=booking.booking_id).first()
                    if existing_review:
                        booking_dict['has_review'] = True
                        booking_dict['review_id'] = existing_review.review_id
                    else:
                        booking_dict['can_review'] = True
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
            
            favorites_query = Favorite.query.filter_by(user_id=session['user_id']).order_by(Favorite.created_at.desc())
            total = favorites_query.count()
            
            favorites = favorites_query.offset((page - 1) * per_page).limit(per_page).all()
            favorites_data = []
            
            for favorite in favorites:
                favorite_dict = favorite.to_dict()
                hotel = Hotel.query.get(favorite.hotel_id)
                
                if hotel:
                    hotel_dict = hotel.to_dict()
                    
                    # Tính giá phòng thấp nhất
                    min_price = db.session.query(func.min(Room.base_price))\
                        .filter(Room.hotel_id == hotel.hotel_id)\
                        .filter(Room.status == 'available')\
                        .scalar() or 0
                    hotel_dict['price_from'] = int(min_price)
                    
                    # Đếm số lượng đánh giá
                    review_count = Review.query.filter_by(hotel_id=hotel.hotel_id, status='active').count()
                    hotel_dict['review_count'] = review_count
                    
                    # Tính điểm đánh giá trung bình
                    avg_rating = db.session.query(func.avg(Review.rating))\
                        .filter_by(hotel_id=hotel.hotel_id, status='active')\
                        .scalar()
                    try:
                        avg_rating_float = float(avg_rating) if avg_rating is not None else 0.0
                    except (TypeError, ValueError):
                        avg_rating_float = 0.0
                    hotel_dict['rating'] = round(avg_rating_float, 1) if avg_rating_float > 0 else 0.0
                    
                    # Lấy hình ảnh đầu tiên
                    primary_image = HotelImage.query.filter_by(hotel_id=hotel.hotel_id, is_primary=True).first()
                    if not primary_image:
                        primary_image = HotelImage.query.filter_by(hotel_id=hotel.hotel_id).order_by(HotelImage.display_order).first()
                    hotel_dict['image_url'] = primary_image.image_url if primary_image else None
                    
                    favorite_dict['hotel'] = hotel_dict
                else:
                    favorite_dict['hotel'] = None
                
                favorites_data.append(favorite_dict)
            
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