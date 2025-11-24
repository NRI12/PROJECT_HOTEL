from flask import request, session
from app import db
from app.models.room import Room
from app.models.room_image import RoomImage
from app.models.amenity import Amenity
from app.models.hotel import Hotel
from app.models.booking_detail import BookingDetail
from app.schemas.room_schema import AmenityCreateSchema, AmenityUpdateSchema
from app.schemas.room_schema import RoomCreateSchema, RoomUpdateSchema, RoomAmenitySchema, RoomStatusSchema
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from datetime import datetime, date
from sqlalchemy import and_, or_
import os
from app.models.room_type import RoomType
from app.models.user import User
from app.schemas.room_schema import RoomTypeCreateSchema, RoomTypeUpdateSchema

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
            
            # Convert amenity_ids to list if it's a single string
            if 'amenity_ids' in data and isinstance(data['amenity_ids'], str):
                data['amenity_ids'] = [data['amenity_ids']]
            
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
            # Get form data
            data = RoomController._get_request_data()
            
            # Validate required fields
            required_fields = ['hotel_id', 'room_type_id', 'room_name', 'base_price', 'max_guests']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            # Check hotel ownership
            hotel = Hotel.query.get(data['hotel_id'])
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            if hotel.owner_id != session['user_id']:
                return error_response('Không có quyền tạo phòng cho khách sạn này', 403)
            
            # Validate room data
            schema = RoomCreateSchema()
            validated_data = schema.load(data)
            
            # Create room
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
                status='available'
            )
            
            db.session.add(room)
            db.session.flush()  # Get room_id without committing
            
            # Handle image uploads
            if 'images' in request.files:
                files = request.files.getlist('images')
                allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
                
                for idx, file in enumerate(files):
                    if file.filename == '':
                        continue
                    
                    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                        from werkzeug.utils import secure_filename
                        import os
                        from datetime import datetime
                        
                        filename = secure_filename(f"room_{room.room_id}_{datetime.now().timestamp()}_{file.filename}")
                        upload_folder = os.path.join('uploads', 'rooms')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        file_path = os.path.join(upload_folder, filename)
                        file.save(file_path)
                        
                        image = RoomImage(
                            room_id=room.room_id,
                            image_url=f"/uploads/rooms/{filename}",
                            is_primary=(idx == 0),
                            display_order=idx
                        )
                        db.session.add(image)
            
            # Handle amenities
            if validated_data.get('amenity_ids'):
                amenities = Amenity.query.filter(
                    Amenity.amenity_id.in_(validated_data['amenity_ids'])
                ).all()
                room.amenities = amenities
            
            db.session.commit()
            
            return success_response(
                data={'room': room.to_dict()},
                message='Tạo phòng thành công',
                status_code=201
            )
            
        except ValidationError as e:
            db.session.rollback()
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
            
            # Update basic fields
            for key, value in validated_data.items():
                if key != 'amenity_ids' and hasattr(room, key):
                    setattr(room, key, value)
            
            # Handle image uploads
            if 'images' in request.files:
                files = request.files.getlist('images')
                allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
                
                for idx, file in enumerate(files):
                    if file.filename == '':
                        continue
                    
                    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                        from werkzeug.utils import secure_filename
                        import os
                        from datetime import datetime
                        
                        filename = secure_filename(f"room_{room.room_id}_{datetime.now().timestamp()}_{file.filename}")
                        upload_folder = os.path.join('uploads', 'rooms')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        file_path = os.path.join(upload_folder, filename)
                        file.save(file_path)
                        
                        # Set as primary only if no images exist
                        is_primary = len(room.images) == 0
                        
                        image = RoomImage(
                            room_id=room.room_id,
                            image_url=f"/uploads/rooms/{filename}",
                            is_primary=is_primary,
                            display_order=len(room.images) + idx
                        )
                        db.session.add(image)
            
            # Handle amenities
            if validated_data.get('amenity_ids'):
                amenities = Amenity.query.filter(
                    Amenity.amenity_id.in_(validated_data['amenity_ids'])
                ).all()
                room.amenities = amenities
            
            db.session.commit()
            
            return success_response(
                data={'room': room.to_dict()},
                message='Cập nhật phòng thành công'
            )
            
        except ValidationError as e:
            db.session.rollback()
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
            
            # Check if room is already booked in the date range
            has_booking = db.session.query(BookingDetail).join(
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
            ).first() is not None
            
            is_available = not has_booking and room.status == 'available'
            
            return success_response(data={
                'room_id': room_id,
                'check_in': check_in_str,
                'check_out': check_out_str,
                'is_available': is_available,
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
    @staticmethod
    def list_room_types():
        try:
            room_types = RoomType.query.all()
            room_types_data = [rt.to_dict() for rt in room_types]
            return success_response(data={'room_types': room_types_data})
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách loại phòng: {str(e)}', 500)
    
    @staticmethod
    def create_room_type():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name != 'admin':
            return error_response('Không có quyền tạo loại phòng', 403)
        
        try:
            data = RoomController._get_request_data()
            
            required_fields = ['type_name']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = RoomTypeCreateSchema()
            validated_data = schema.load(data)
            
            existing = RoomType.query.filter_by(type_name=validated_data['type_name']).first()
            if existing:
                return error_response('Tên loại phòng đã tồn tại', 409)
            
            room_type = RoomType(
                type_name=validated_data['type_name'],
                description=validated_data.get('description')
            )
            
            db.session.add(room_type)
            db.session.commit()
            
            return success_response(
                data={'room_type': room_type.to_dict()},
                message='Tạo loại phòng thành công',
                status_code=201
            )
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo loại phòng thất bại: {str(e)}', 500)
    
    @staticmethod
    def update_room_type(type_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name != 'admin':
            return error_response('Không có quyền cập nhật loại phòng', 403)
        
        try:
            room_type = RoomType.query.get(type_id)
            if not room_type:
                return error_response('Không tìm thấy loại phòng', 404)
            
            data = RoomController._get_request_data()
            schema = RoomTypeUpdateSchema()
            validated_data = schema.load(data)
            
            if 'type_name' in validated_data:
                existing = RoomType.query.filter(
                    RoomType.type_name == validated_data['type_name'],
                    RoomType.type_id != type_id
                ).first()
                if existing:
                    return error_response('Tên loại phòng đã tồn tại', 409)
            
            for key, value in validated_data.items():
                if hasattr(room_type, key):
                    setattr(room_type, key, value)
            
            db.session.commit()
            
            return success_response(
                data={'room_type': room_type.to_dict()},
                message='Cập nhật loại phòng thành công'
            )
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật loại phòng thất bại: {str(e)}', 500)
    
    @staticmethod
    def delete_room_type(type_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name != 'admin':
            return error_response('Không có quyền xóa loại phòng', 403)
        
        try:
            room_type = RoomType.query.get(type_id)
            if not room_type:
                return error_response('Không tìm thấy loại phòng', 404)
            
            if room_type.rooms:
                return error_response('Không thể xóa loại phòng đang được sử dụng', 400)
            
            db.session.delete(room_type)
            db.session.commit()
            
            return success_response(message='Xóa loại phòng thành công')
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa loại phòng thất bại: {str(e)}', 500)
    @staticmethod
    def get_room_type(type_id):
        try:
            room_type = RoomType.query.get(type_id)
            if not room_type:
                return error_response('Không tìm thấy loại phòng', 404)
            return success_response(data={'room_type': room_type.to_dict()})
        except Exception as e:
            return error_response(f'Lỗi khi lấy loại phòng: {str(e)}', 500)
    
    @staticmethod
    def list_amenities():
        try:
            amenities = Amenity.query.all()
            amenities_data = [a.to_dict() for a in amenities]
            return success_response(data={'amenities': amenities_data})
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách tiện nghi: {str(e)}', 500)
    
    @staticmethod
    def get_amenity(amenity_id):
        try:
            amenity = Amenity.query.get(amenity_id)
            if not amenity:
                return error_response('Không tìm thấy tiện nghi', 404)
            return success_response(data={'amenity': amenity.to_dict()})
        except Exception as e:
            return error_response(f'Lỗi khi lấy tiện nghi: {str(e)}', 500)
    
    @staticmethod
    def create_amenity():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name != 'admin':
            return error_response('Không có quyền tạo tiện nghi', 403)
        
        try:
            data = RoomController._get_request_data()
            
            required_fields = ['amenity_name']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = AmenityCreateSchema()
            validated_data = schema.load(data)
            
            existing = Amenity.query.filter_by(amenity_name=validated_data['amenity_name']).first()
            if existing:
                return error_response('Tên tiện nghi đã tồn tại', 409)
            
            amenity = Amenity(
                amenity_name=validated_data['amenity_name'],
                icon=validated_data.get('icon'),
                category=validated_data.get('category', 'both')
            )
            
            db.session.add(amenity)
            db.session.commit()
            
            return success_response(
                data={'amenity': amenity.to_dict()},
                message='Tạo tiện nghi thành công',
                status_code=201
            )
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo tiện nghi thất bại: {str(e)}', 500)
    
    @staticmethod
    def update_amenity(amenity_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name != 'admin':
            return error_response('Không có quyền cập nhật tiện nghi', 403)
        
        try:
            amenity = Amenity.query.get(amenity_id)
            if not amenity:
                return error_response('Không tìm thấy tiện nghi', 404)
            
            data = RoomController._get_request_data()
            schema = AmenityUpdateSchema()
            validated_data = schema.load(data)
            
            if 'amenity_name' in validated_data:
                existing = Amenity.query.filter(
                    Amenity.amenity_name == validated_data['amenity_name'],
                    Amenity.amenity_id != amenity_id
                ).first()
                if existing:
                    return error_response('Tên tiện nghi đã tồn tại', 409)
            
            for key, value in validated_data.items():
                if hasattr(amenity, key):
                    setattr(amenity, key, value)
            
            db.session.commit()
            
            return success_response(
                data={'amenity': amenity.to_dict()},
                message='Cập nhật tiện nghi thành công'
            )
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật tiện nghi thất bại: {str(e)}', 500)
    
    @staticmethod
    def delete_amenity(amenity_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name != 'admin':
            return error_response('Không có quyền xóa tiện nghi', 403)
        
        try:
            amenity = Amenity.query.get(amenity_id)
            if not amenity:
                return error_response('Không tìm thấy tiện nghi', 404)
            
            if amenity.rooms or amenity.hotels:
                return error_response('Không thể xóa tiện nghi đang được sử dụng', 400)
            
            db.session.delete(amenity)
            db.session.commit()
            
            return success_response(message='Xóa tiện nghi thành công')
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa tiện nghi thất bại: {str(e)}', 500)