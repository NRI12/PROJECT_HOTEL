from flask import request, session
from app import db
from app.models.hotel import Hotel
from app.models.hotel_image import HotelImage
from app.models.hotel_amenity import hotel_amenities
from app.models.amenity import Amenity
from app.models.room import Room
from app.models.review import Review
from app.models.cancellation_policy import CancellationPolicy
from app.schemas.hotel_schema import (
    HotelCreateSchema, HotelUpdateSchema, HotelSearchSchema,
    AmenityUpdateSchema, PolicyCreateSchema
)
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from datetime import datetime, time
import os

class HotelController:
    
    @staticmethod
    def _get_request_data():
        """Chỉ lấy dữ liệu từ form-data, không dùng JSON"""
        if request.form:
            data = dict(request.form)
            # Xử lý các trường có nhiều giá trị (như amenity_ids)
            for key, value in data.items():
                if isinstance(value, list):
                    # Nếu là amenity_ids, giữ nguyên list để schema xử lý
                    if key == 'amenity_ids':
                        continue
                    # Các trường khác: nếu là list với 1 phần tử, chuyển thành string
                    elif len(value) == 1:
                        data[key] = value[0]
            return data
        else:
            return {}
    
    @staticmethod
    def list_hotels():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            city = request.args.get('city')
            min_rating = request.args.get('min_rating', type=int)
            max_rating = request.args.get('max_rating', type=int)
            is_featured = request.args.get('is_featured', type=lambda v: v.lower() == 'true')
            search = request.args.get('search')
            
            query = Hotel.query.filter_by(status='active')
            
            if city:
                query = query.filter(Hotel.city.ilike(f'%{city}%'))
            if min_rating:
                query = query.filter(Hotel.star_rating >= min_rating)
            if max_rating:
                query = query.filter(Hotel.star_rating <= max_rating)
            if is_featured is not None:
                query = query.filter_by(is_featured=is_featured)
            if search:
                query = query.filter(
                    db.or_(
                        Hotel.hotel_name.ilike(f'%{search}%'),
                        Hotel.address.ilike(f'%{search}%'),
                        Hotel.description.ilike(f'%{search}%')
                    )
                )
            
            total = query.count()
            hotels = query.offset((page - 1) * per_page).limit(per_page).all()
            hotels_data = []
            
            for hotel in hotels:
                hotel_dict = hotel.to_dict()
                hotel_dict['images'] = [img.to_dict() for img in hotel.images]
                hotels_data.append(hotel_dict)
            
            return paginated_response(hotels_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách khách sạn: {str(e)}', 500)
    
    @staticmethod
    def get_featured_hotels():
        try:
            limit = request.args.get('limit', 10, type=int)
            
            hotels = Hotel.query.filter_by(status='active', is_featured=True).limit(limit).all()
            hotels_data = []
            
            for hotel in hotels:
                hotel_dict = hotel.to_dict()
                hotel_dict['images'] = [img.to_dict() for img in hotel.images]
                hotels_data.append(hotel_dict)
            
            return success_response(data={'hotels': hotels_data})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy khách sạn nổi bật: {str(e)}', 500)
    
    @staticmethod
    def get_hotel(hotel_id):
        try:
            hotel = Hotel.query.get(hotel_id)
            
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            hotel_dict = hotel.to_dict()
            hotel_dict['images'] = [img.to_dict() for img in hotel.images]
            hotel_dict['amenities'] = [amenity.to_dict() for amenity in hotel.amenities]
            hotel_dict['cancellation_policies'] = [policy.to_dict() for policy in hotel.cancellation_policies]
            
            avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(hotel_id=hotel_id, status='active').scalar()
            hotel_dict['average_rating'] = float(avg_rating) if avg_rating else None
            hotel_dict['review_count'] = Review.query.filter_by(hotel_id=hotel_id, status='active').count()
            
            return success_response(data={'hotel': hotel_dict})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy chi tiết khách sạn: {str(e)}', 500)
    
    @staticmethod
    def create_hotel():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            data = HotelController._get_request_data()
            
            required_fields = ['hotel_name', 'address', 'city']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = HotelCreateSchema()
            validated_data = schema.load(data)
            
            hotel = Hotel(
                owner_id=session['user_id'],
                hotel_name=validated_data['hotel_name'],
                description=validated_data.get('description'),
                address=validated_data['address'],
                city=validated_data['city'],
                district=validated_data.get('district'),
                ward=validated_data.get('ward'),
                latitude=validated_data.get('latitude'),
                longitude=validated_data.get('longitude'),
                star_rating=validated_data.get('star_rating'),
                phone=validated_data.get('phone'),
                email=validated_data.get('email'),
                check_in_time=validated_data.get('check_in_time', time(14, 0)),
                check_out_time=validated_data.get('check_out_time', time(12, 0)),
                status='pending'
            )
            
            db.session.add(hotel)
            db.session.commit()
            
            return success_response(
                data={'hotel': hotel.to_dict()},
                message='Tạo khách sạn thành công. Đang chờ duyệt.',
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo khách sạn thất bại: {str(e)}', 500)
    
    @staticmethod
    def update_hotel(hotel_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            hotel = Hotel.query.get(hotel_id)
            
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền cập nhật khách sạn này', 403)
            
            data = HotelController._get_request_data()
            schema = HotelUpdateSchema()
            validated_data = schema.load(data)
            
            for key, value in validated_data.items():
                if hasattr(hotel, key):
                    setattr(hotel, key, value)
            
            db.session.commit()
            
            return success_response(
                data={'hotel': hotel.to_dict()},
                message='Cập nhật khách sạn thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật khách sạn thất bại: {str(e)}', 500)
    
    @staticmethod
    def delete_hotel(hotel_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            hotel = Hotel.query.get(hotel_id)
            
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền xóa khách sạn này', 403)
            
            db.session.delete(hotel)
            db.session.commit()
            
            return success_response(message='Xóa khách sạn thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa khách sạn thất bại: {str(e)}', 500)
    
    @staticmethod
    def upload_images(hotel_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            hotel = Hotel.query.get(hotel_id)
            
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền tải ảnh cho khách sạn này', 403)
            
            if 'images' not in request.files:
                return error_response('Không có file được chọn', 400)
            
            files = request.files.getlist('images')
            if not files:
                return error_response('Không có file được chọn', 400)
            
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
            uploaded_images = []
            
            for file in files:
                if file.filename == '':
                    continue
                
                if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                    continue
                
                filename = secure_filename(f"hotel_{hotel_id}_{datetime.now().timestamp()}_{file.filename}")
                upload_folder = os.path.join('uploads', 'hotels')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                is_primary = len(hotel.images) == 0
                
                image = HotelImage(
                    hotel_id=hotel_id,
                    image_url=f"/uploads/hotels/{filename}",
                    is_primary=is_primary,
                    display_order=len(hotel.images)
                )
                
                db.session.add(image)
                uploaded_images.append(image)
            
            db.session.commit()
            
            return success_response(
                data={'images': [img.to_dict() for img in uploaded_images]},
                message='Tải ảnh thành công'
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tải ảnh thất bại: {str(e)}', 500)
    
    @staticmethod
    def delete_image(hotel_id, image_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            hotel = Hotel.query.get(hotel_id)
            
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền xóa ảnh', 403)
            
            image = HotelImage.query.filter_by(image_id=image_id, hotel_id=hotel_id).first()
            
            if not image:
                return error_response('Không tìm thấy ảnh', 404)
            
            db.session.delete(image)
            db.session.commit()
            
            return success_response(message='Xóa ảnh thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa ảnh thất bại: {str(e)}', 500)
    
    @staticmethod
    def set_primary_image(hotel_id, image_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            hotel = Hotel.query.get(hotel_id)
            
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền thay đổi ảnh chính', 403)
            
            image = HotelImage.query.filter_by(image_id=image_id, hotel_id=hotel_id).first()
            
            if not image:
                return error_response('Không tìm thấy ảnh', 404)
            
            for img in hotel.images:
                img.is_primary = False
            
            image.is_primary = True
            db.session.commit()
            
            return success_response(message='Đặt ảnh chính thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Đặt ảnh chính thất bại: {str(e)}', 500)
    
    @staticmethod
    def get_hotel_reviews(hotel_id):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            hotel = Hotel.query.get(hotel_id)
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            reviews_query = Review.query.filter_by(hotel_id=hotel_id, status='active').order_by(Review.created_at.desc())
            total = reviews_query.count()
            
            reviews = reviews_query.offset((page - 1) * per_page).limit(per_page).all()
            reviews_data = []
            
            for review in reviews:
                review_dict = review.to_dict()
                review_dict['user'] = review.user.to_dict() if review.user else None
                reviews_data.append(review_dict)
            
            return paginated_response(reviews_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy đánh giá: {str(e)}', 500)
    
    @staticmethod
    def get_hotel_rooms(hotel_id):
        try:
            hotel = Hotel.query.get(hotel_id)
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            rooms = Room.query.filter_by(hotel_id=hotel_id, status='available').all()
            rooms_data = []
            
            for room in rooms:
                room_dict = room.to_dict()
                room_dict['images'] = [img.to_dict() for img in room.images]
                room_dict['amenities'] = [amenity.to_dict() for amenity in room.amenities]
                rooms_data.append(room_dict)
            
            return success_response(data={'rooms': rooms_data})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách phòng: {str(e)}', 500)
    
    @staticmethod
    def get_hotel_amenities(hotel_id):
        try:
            hotel = Hotel.query.get(hotel_id)
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            amenities_data = [amenity.to_dict() for amenity in hotel.amenities]
            
            return success_response(data={'amenities': amenities_data})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy tiện nghi: {str(e)}', 500)
    
    @staticmethod
    def update_hotel_amenities(hotel_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            hotel = Hotel.query.get(hotel_id)
            
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền cập nhật tiện nghi', 403)
            
            data = HotelController._get_request_data()
            schema = AmenityUpdateSchema()
            validated_data = schema.load(data)
            
            amenity_ids = validated_data['amenity_ids']
            amenities = Amenity.query.filter(Amenity.amenity_id.in_(amenity_ids)).all()
            
            hotel.amenities = amenities
            db.session.commit()
            
            return success_response(
                data={'amenities': [amenity.to_dict() for amenity in hotel.amenities]},
                message='Cập nhật tiện nghi thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật tiện nghi thất bại: {str(e)}', 500)
    
    @staticmethod
    def get_hotel_policies(hotel_id):
        try:
            hotel = Hotel.query.get(hotel_id)
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            policies_data = [policy.to_dict() for policy in hotel.cancellation_policies]
            
            return success_response(data={'policies': policies_data})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy chính sách: {str(e)}', 500)
    
    @staticmethod
    def create_hotel_policy(hotel_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            hotel = Hotel.query.get(hotel_id)
            
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền tạo chính sách', 403)
            
            data = HotelController._get_request_data()
            schema = PolicyCreateSchema()
            validated_data = schema.load(data)
            
            policy = CancellationPolicy(
                hotel_id=hotel_id,
                name=validated_data['name'],
                description=validated_data.get('description'),
                hours_before_checkin=validated_data['hours_before_checkin'],
                refund_percentage=validated_data['refund_percentage']
            )
            
            db.session.add(policy)
            db.session.commit()
            
            return success_response(
                data={'policy': policy.to_dict()},
                message='Tạo chính sách thành công',
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo chính sách thất bại: {str(e)}', 500)