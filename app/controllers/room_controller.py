from flask import request, session
from app import db
from app.models.room import Room
from app.models.room_image import RoomImage
from app.models.amenity import Amenity
from app.models.hotel import Hotel
from app.models.booking_detail import BookingDetail
from app.schemas.room_schema import RoomCreateSchema, RoomUpdateSchema, RoomAmenitySchema, RoomStatusSchema
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from datetime import datetime, date
from sqlalchemy import and_, or_
import os

class RoomController:
    
    @staticmethod
    def _get_request_data():
        if request.form:
            data = dict(request.form)
            for key, value in data.items():
                if isinstance(value, list):
                    if key == 'amenity_ids':
                        continue
                    elif len(value) == 1:
                        data[key] = value[0]
            return data
        elif request.is_json:
            return request.get_json()
        else:
            return {}
    
    @staticmethod
    def list_rooms():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            hotel_id = request.args.get('hotel_id', type=int)
            status = request.args.get('status')
            
            query = Room.query
            
            if hotel_id:
                query = query.filter_by(hotel_id=hotel_id)
            
            if status:
                query = query.filter_by(status=status)
            
            total = query.count()
            rooms = query.offset((page - 1) * per_page).limit(per_page).all()
            
            rooms_data = []
            for room in rooms:
                room_dict = room.to_dict()
                room_dict['hotel'] = room.hotel.to_dict() if room.hotel else None
                room_dict['room_type'] = room.room_type.to_dict() if room.room_type else None
                room_dict['images'] = [img.to_dict() for img in room.images]
                rooms_data.append(room_dict)
            
            return paginated_response(rooms_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách phòng: {str(e)}', 500)
    
    @staticmethod
    def get_room(room_id):
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            room_dict = room.to_dict()
            room_dict['hotel'] = room.hotel.to_dict() if room.hotel else None
            room_dict['room_type'] = room.room_type.to_dict() if room.room_type else None
            room_dict['images'] = [img.to_dict() for img in room.images]
            room_dict['amenities'] = [amenity.to_dict() for amenity in room.amenities]
            
            return success_response(data={'room': room_dict})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy chi tiết phòng: {str(e)}', 500)
    
    @staticmethod
    def create_room():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            data = RoomController._get_request_data()
            
            required_fields = ['hotel_id', 'room_type_id', 'room_name', 'base_price', 'max_guests']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            hotel = Hotel.query.get(data['hotel_id'])
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền tạo phòng cho khách sạn này', 403)
            
            schema = RoomCreateSchema()
            validated_data = schema.load(data)
            
            room = Room(
                hotel_id=validated_data['hotel_id'],
                room_type_id=validated_data['room_type_id'],
                room_number=validated_data.get('room_number'),
                room_name=validated_data['room_name'],
                description=validated_data.get('description'),
                area=validated_data.get('area'),
                max_guests=validated_data['max_guests'],
                num_beds=validated_data.get('num_beds', 1),
                bed_type=validated_data.get('bed_type'),
                base_price=validated_data['base_price'],
                weekend_price=validated_data.get('weekend_price'),
                quantity=validated_data.get('quantity', 1),
                status='available'
            )
            
            db.session.add(room)
            db.session.commit()
            
            return success_response(
                data={'room': room.to_dict()},
                message='Tạo phòng thành công',
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo phòng thất bại: {str(e)}', 500)
    
    @staticmethod
    def update_room(room_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            if room.hotel.owner_id != session['user_id']:
                return error_response('Không có quyền cập nhật phòng này', 403)
            
            data = RoomController._get_request_data()
            schema = RoomUpdateSchema()
            validated_data = schema.load(data)
            
            for key, value in validated_data.items():
                if hasattr(room, key):
                    setattr(room, key, value)
            
            db.session.commit()
            
            return success_response(
                data={'room': room.to_dict()},
                message='Cập nhật phòng thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật phòng thất bại: {str(e)}', 500)
    
    @staticmethod
    def delete_room(room_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            if room.hotel.owner_id != session['user_id']:
                return error_response('Không có quyền xóa phòng này', 403)
            
            db.session.delete(room)
            db.session.commit()
            
            return success_response(message='Xóa phòng thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa phòng thất bại: {str(e)}', 500)
    
    @staticmethod
    def upload_images(room_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            if room.hotel.owner_id != session['user_id']:
                return error_response('Không có quyền tải ảnh cho phòng này', 403)
            
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
                
                filename = secure_filename(f"room_{room_id}_{datetime.now().timestamp()}_{file.filename}")
                upload_folder = os.path.join('uploads', 'rooms')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                is_primary = len(room.images) == 0
                
                image = RoomImage(
                    room_id=room_id,
                    image_url=f"/uploads/rooms/{filename}",
                    is_primary=is_primary,
                    display_order=len(room.images)
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
    def delete_image(room_id, image_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            if room.hotel.owner_id != session['user_id']:
                return error_response('Không có quyền xóa ảnh', 403)
            
            image = RoomImage.query.filter_by(image_id=image_id, room_id=room_id).first()
            if not image:
                return error_response('Không tìm thấy ảnh', 404)
            
            db.session.delete(image)
            db.session.commit()
            
            return success_response(message='Xóa ảnh thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa ảnh thất bại: {str(e)}', 500)
    
    @staticmethod
    def get_room_amenities(room_id):
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            amenities_data = [amenity.to_dict() for amenity in room.amenities]
            
            return success_response(data={'amenities': amenities_data})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy tiện nghi: {str(e)}', 500)
    
    @staticmethod
    def update_room_amenities(room_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            if room.hotel.owner_id != session['user_id']:
                return error_response('Không có quyền cập nhật tiện nghi', 403)
            
            data = RoomController._get_request_data()
            schema = RoomAmenitySchema()
            validated_data = schema.load(data)
            
            amenity_ids = validated_data['amenity_ids']
            amenities = Amenity.query.filter(Amenity.amenity_id.in_(amenity_ids)).all()
            
            room.amenities = amenities
            db.session.commit()
            
            return success_response(
                data={'amenities': [amenity.to_dict() for amenity in room.amenities]},
                message='Cập nhật tiện nghi thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật tiện nghi thất bại: {str(e)}', 500)
    
    @staticmethod
    def check_availability(room_id):
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            check_in_str = request.args.get('check_in')
            check_out_str = request.args.get('check_out')
            
            if not check_in_str or not check_out_str:
                return error_response('Thiếu ngày check_in hoặc check_out', 400)
            
            try:
                check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('Định dạng ngày không hợp lệ (YYYY-MM-DD)', 400)
            
            if check_in >= check_out:
                return error_response('Ngày check_out phải sau ngày check_in', 400)
            
            if check_in < date.today():
                return error_response('Ngày check_in không thể là quá khứ', 400)
            
            booked_count = db.session.query(db.func.sum(BookingDetail.quantity)).join(
                BookingDetail.booking
            ).filter(
                and_(
                    BookingDetail.room_id == room_id,
                    BookingDetail.booking.has(
                        and_(
                            or_(
                                and_(
                                    BookingDetail.booking.property.mapper.c.check_in_date <= check_in,
                                    BookingDetail.booking.property.mapper.c.check_out_date > check_in
                                ),
                                and_(
                                    BookingDetail.booking.property.mapper.c.check_in_date < check_out,
                                    BookingDetail.booking.property.mapper.c.check_out_date >= check_out
                                ),
                                and_(
                                    BookingDetail.booking.property.mapper.c.check_in_date >= check_in,
                                    BookingDetail.booking.property.mapper.c.check_out_date <= check_out
                                )
                            ),
                            BookingDetail.booking.property.mapper.c.status.in_(['pending', 'confirmed', 'checked_in'])
                        )
                    )
                )
            ).scalar() or 0
            
            available_quantity = room.quantity - booked_count
            is_available = available_quantity > 0 and room.status == 'available'
            
            return success_response(data={
                'room_id': room_id,
                'check_in': check_in_str,
                'check_out': check_out_str,
                'is_available': is_available,
                'total_quantity': room.quantity,
                'available_quantity': max(0, available_quantity),
                'status': room.status
            })
            
        except Exception as e:
            return error_response(f'Lỗi khi kiểm tra phòng trống: {str(e)}', 500)
    
    @staticmethod
    def update_room_status(room_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            room = Room.query.get(room_id)
            if not room:
                return error_response('Không tìm thấy phòng', 404)
            
            if room.hotel.owner_id != session['user_id']:
                return error_response('Không có quyền cập nhật trạng thái phòng', 403)
            
            data = RoomController._get_request_data()
            schema = RoomStatusSchema()
            validated_data = schema.load(data)
            
            room.status = validated_data['status']
            db.session.commit()
            
            return success_response(
                data={'room': room.to_dict()},
                message='Cập nhật trạng thái phòng thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật trạng thái thất bại: {str(e)}', 500)