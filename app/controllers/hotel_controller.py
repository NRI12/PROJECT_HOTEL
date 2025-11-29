from flask import request, session
from app import db
from app.models.hotel import Hotel
from app.models.hotel_image import HotelImage
from app.models.hotel_amenity import hotel_amenities
from app.models.amenity import Amenity
from app.models.room import Room
from app.models.review import Review
from app.models.booking import Booking
from app.models.booking_detail import BookingDetail
from app.models.cancellation_policy import CancellationPolicy
from app.schemas.hotel_schema import (
    HotelCreateSchema, HotelUpdateSchema, HotelSearchSchema,
    AmenityUpdateSchema, PolicyCreateSchema
)
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from datetime import datetime, time, date
import os
import uuid

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
            
            # Tính avg_rating và review_count
            from sqlalchemy import func
            avg_rating = db.session.query(func.avg(Review.rating))\
                .filter(Review.hotel_id == hotel_id, Review.status == 'active')\
                .scalar()
            review_count = Review.query.filter_by(
                hotel_id=hotel_id, 
                status='active'
            ).count()
            # Chuyển đổi avg_rating sang float trước khi làm tròn
            if avg_rating is not None:
                avg_rating_float = float(avg_rating)
                hotel_dict['avg_rating'] = round(avg_rating_float, 1)
                hotel_dict['average_rating'] = round(avg_rating_float, 1)  # Keep for backward compatibility
            else:
                hotel_dict['avg_rating'] = 0
                hotel_dict['average_rating'] = 0
            hotel_dict['review_count'] = review_count
            
            # Tính đánh giá trung bình theo từng tiêu chí
            avg_cleanliness = db.session.query(func.avg(Review.cleanliness_rating))\
                .filter(Review.hotel_id == hotel_id, Review.status == 'active', Review.cleanliness_rating.isnot(None))\
                .scalar()
            avg_service = db.session.query(func.avg(Review.service_rating))\
                .filter(Review.hotel_id == hotel_id, Review.status == 'active', Review.service_rating.isnot(None))\
                .scalar()
            avg_facilities = db.session.query(func.avg(Review.facilities_rating))\
                .filter(Review.hotel_id == hotel_id, Review.status == 'active', Review.facilities_rating.isnot(None))\
                .scalar()
            avg_location = db.session.query(func.avg(Review.location_rating))\
                .filter(Review.hotel_id == hotel_id, Review.status == 'active', Review.location_rating.isnot(None))\
                .scalar()
            
            hotel_dict['avg_cleanliness_rating'] = round(float(avg_cleanliness), 1) if avg_cleanliness is not None else None
            hotel_dict['avg_service_rating'] = round(float(avg_service), 1) if avg_service is not None else None
            hotel_dict['avg_facilities_rating'] = round(float(avg_facilities), 1) if avg_facilities is not None else None
            hotel_dict['avg_location_rating'] = round(float(avg_location), 1) if avg_location is not None else None
            
            # Lấy rooms với xử lý lỗi
            rooms_data = []
            try:
                rooms_query = Room.query.filter_by(hotel_id=hotel_id, status='available').order_by(Room.base_price.asc()).all()
                for room in rooms_query:
                    try:
                        room_dict = room.to_dict()
                        room_dict['images'] = [img.to_dict() for img in room.images]
                        room_dict['amenities'] = [amenity.to_dict() for amenity in room.amenities]
                        room_dict['room_type'] = room.room_type.to_dict() if room.room_type else None
                        rooms_data.append(room_dict)
                    except Exception as e:
                        print(f"Error processing room {room.room_id}: {str(e)}")
                        continue
            except Exception as e:
                print(f"Error getting rooms: {str(e)}")
                rooms_data = []

            # Lấy reviews với xử lý lỗi riêng
            reviews_data = []
            try:
                from sqlalchemy.orm import joinedload
                from app.models.room_type import RoomType
                
                recent_reviews = Review.query.options(
                    joinedload(Review.user),
                    joinedload(Review.booking).joinedload(Booking.booking_details).joinedload(BookingDetail.room).joinedload(Room.room_type)
                ).filter_by(hotel_id=hotel_id, status='active')\
                .order_by(Review.created_at.desc())\
                .limit(5).all()
                
                for review in recent_reviews:
                    try:
                        review_dict = review.to_dict()
                        # Load user với thông tin đầy đủ
                        if review.user:
                            review_dict['user'] = {
                                'user_id': review.user.user_id,
                                'full_name': review.user.full_name,
                                'email': review.user.email,
                                'name': review.user.full_name or review.user.email,
                                'avatar_url': review.user.avatar_url
                            }
                        else:
                            review_dict['user'] = None
                        
                        # Lấy thông tin phòng từ booking_details qua relationship
                        rooms_info = []
                        try:
                            if review.booking and review.booking.booking_details:
                                for detail in review.booking.booking_details:
                                    try:
                                        # Sử dụng relationship đã được load
                                        if detail.room:
                                            room = detail.room
                                            room_info = {
                                                'room_id': room.room_id,
                                                'room_name': room.room_name if room.room_name else f'Phòng #{room.room_id}',
                                                'room_type': room.room_type.room_type_name if room.room_type and hasattr(room.room_type, 'room_type_name') else None,
                                                'area': float(room.area) if room.area else None,
                                                'max_guests': room.max_guests if room.max_guests else None,
                                                'quantity': detail.quantity if detail.quantity else 1
                                            }
                                            rooms_info.append(room_info)
                                    except Exception as e:
                                        # Bỏ qua nếu không lấy được thông tin phòng
                                        print(f"Error getting room info for detail {detail.detail_id}: {str(e)}")
                                        import traceback
                                        traceback.print_exc()
                                        continue
                        except Exception as e:
                            # Bỏ qua nếu không lấy được booking_details
                            print(f"Error getting booking_details for review {review.review_id}: {str(e)}")
                            import traceback
                            traceback.print_exc()
                        
                        review_dict['rooms'] = rooms_info if rooms_info else []
                        reviews_data.append(review_dict)
                    except Exception as e:
                        # Bỏ qua review nếu có lỗi
                        print(f"Error processing review {review.review_id}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        continue
            except Exception as e:
                # Nếu có lỗi khi lấy reviews, vẫn tiếp tục với reviews_data = []
                print(f"Error getting reviews: {str(e)}")
                import traceback
                traceback.print_exc()
                reviews_data = []

            eligible_bookings = []
            user_id = session.get('user_id')
            if user_id:
                today = date.today()
                
                bookings_query = Booking.query.filter(
                    Booking.user_id == user_id,
                    Booking.hotel_id == hotel_id,
                    Booking.status == 'checked_out',
                    Booking.check_out_date <= today
                ).order_by(Booking.check_out_date.desc()).limit(10).all()

                for booking in bookings_query:
                    has_review = Review.query.filter_by(booking_id=booking.booking_id).first()
                    if has_review:
                        continue

                    booking_dict = booking.to_dict()
                    eligible_bookings.append({
                        'booking_id': booking.booking_id,
                        'booking_code': booking.booking_code,
                        'check_in': booking_dict.get('check_in_date'),
                        'check_out': booking_dict.get('check_out_date'),
                        'created_at': booking_dict.get('created_at')
                    })
            
            return success_response(data={
                'hotel': hotel_dict,
                'rooms': rooms_data,
                'reviews': reviews_data,
                'eligible_bookings': eligible_bookings
            })
            
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
            db.session.flush()  # Flush để có hotel_id
            
            # Xử lý upload hình ảnh nếu có
            uploaded_images = []
            if 'images' in request.files:
                files = request.files.getlist('images')
                if files and files[0].filename != '':
                    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
                    
                    for idx, file in enumerate(files):
                        if file.filename == '':
                            continue
                        
                        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                            continue
                        
                        # Tạo tên file random với UUID
                        file_ext = file.filename.rsplit('.', 1)[1].lower()
                        random_filename = f"{uuid.uuid4().hex}.{file_ext}"
                        
                        upload_folder = os.path.join('uploads', 'hotels')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        file_path = os.path.join(upload_folder, random_filename)
                        file.save(file_path)
                        
                        # Ảnh đầu tiên là ảnh chính
                        is_primary = (idx == 0)
                        
                        image = HotelImage(
                            hotel_id=hotel.hotel_id,
                            image_url=f"/uploads/hotels/{random_filename}",
                            is_primary=is_primary,
                            display_order=idx
                        )
                        
                        db.session.add(image)
                        uploaded_images.append(image)
            
            db.session.commit()
            
            hotel_dict = hotel.to_dict()
            hotel_dict['images'] = [img.to_dict() for img in uploaded_images]
            
            return success_response(
                data={'hotel': hotel_dict},
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
            
            # Xử lý upload hình ảnh nếu có
            uploaded_images = []
            if 'images' in request.files:
                files = request.files.getlist('images')
                if files and files[0].filename != '':
                    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
                    
                    for idx, file in enumerate(files):
                        if file.filename == '':
                            continue
                        
                        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                            continue
                        
                        # Tạo tên file random với UUID
                        file_ext = file.filename.rsplit('.', 1)[1].lower()
                        random_filename = f"{uuid.uuid4().hex}.{file_ext}"
                        
                        upload_folder = os.path.join('uploads', 'hotels')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        file_path = os.path.join(upload_folder, random_filename)
                        file.save(file_path)
                        
                        # Ảnh đầu tiên là primary nếu chưa có ảnh nào
                        is_primary = len(hotel.images) == 0 and idx == 0
                        
                        image = HotelImage(
                            hotel_id=hotel_id,
                            image_url=f"/uploads/hotels/{random_filename}",
                            is_primary=is_primary,
                            display_order=len(hotel.images) + idx
                        )
                        
                        db.session.add(image)
                        uploaded_images.append(image)
            
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
                
                # Tạo tên file random với UUID
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                random_filename = f"{uuid.uuid4().hex}.{file_ext}"
                
                upload_folder = os.path.join('uploads', 'hotels')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, random_filename)
                file.save(file_path)
                
                is_primary = len(hotel.images) == 0
                
                image = HotelImage(
                    hotel_id=hotel_id,
                    image_url=f"/uploads/hotels/{random_filename}",
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
                room_dict['room_type'] = room.room_type.to_dict() if room.room_type else None
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