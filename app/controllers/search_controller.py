from flask import request, session
from app import db
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.booking_detail import BookingDetail
from app.models.search_history import SearchHistory
from app.models.user import User
from app.schemas.search_schema import SearchSchema, AdvancedSearchSchema, CheckAvailabilitySchema
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from datetime import datetime, date
from sqlalchemy import and_, or_, func

class SearchController:
    
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
    def search():
        try:
            data = SearchController._get_request_data()
            
            schema = SearchSchema()
            validated_data = schema.load(data)
            
            query = Hotel.query.filter_by(status='active')
            
            if validated_data.get('destination'):
                destination = validated_data['destination']
                query = query.filter(
                    or_(
                        Hotel.city.ilike(f'%{destination}%'),
                        Hotel.address.ilike(f'%{destination}%'),
                        Hotel.hotel_name.ilike(f'%{destination}%')
                    )
                )
            
            if validated_data.get('min_price'):
                query = query.join(Room).filter(Room.base_price >= validated_data['min_price'])
            
            if validated_data.get('max_price'):
                query = query.join(Room).filter(Room.base_price <= validated_data['max_price'])
            
            if validated_data.get('star_rating'):
                query = query.filter(Hotel.star_rating >= validated_data['star_rating'])
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            total = query.distinct().count()
            hotels = query.distinct().offset((page - 1) * per_page).limit(per_page).all()
            
            hotels_data = []
            for hotel in hotels:
                hotel_dict = hotel.to_dict()
                hotel_dict['images'] = [img.to_dict() for img in hotel.images]
                hotels_data.append(hotel_dict)
            
            if 'user_id' in session and validated_data.get('destination'):
                history = SearchHistory(
                    user_id=session['user_id'],
                    destination=validated_data['destination'],
                    check_in_date=validated_data.get('check_in'),
                    check_out_date=validated_data.get('check_out'),
                    num_guests=validated_data.get('num_guests')
                )
                db.session.add(history)
                db.session.commit()
            
            return paginated_response(hotels_data, page, per_page, total)
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            return error_response(f'Lỗi tìm kiếm: {str(e)}', 500)
    
    @staticmethod
    def advanced_search():
        try:
            data = SearchController._get_request_data()
            
            schema = AdvancedSearchSchema()
            validated_data = schema.load(data)
            
            query = Hotel.query.filter_by(status='active')
            
            if validated_data.get('destination'):
                destination = validated_data['destination']
                query = query.filter(
                    or_(
                        Hotel.city.ilike(f'%{destination}%'),
                        Hotel.address.ilike(f'%{destination}%'),
                        Hotel.hotel_name.ilike(f'%{destination}%')
                    )
                )
            
            if validated_data.get('star_rating'):
                query = query.filter(Hotel.star_rating >= validated_data['star_rating'])
            
            if validated_data.get('amenity_ids'):
                for amenity_id in validated_data['amenity_ids']:
                    query = query.filter(Hotel.amenities.any(amenity_id=amenity_id))
            
            if validated_data.get('min_price') or validated_data.get('max_price'):
                query = query.join(Room)
                if validated_data.get('min_price'):
                    query = query.filter(Room.base_price >= validated_data['min_price'])
                if validated_data.get('max_price'):
                    query = query.filter(Room.base_price <= validated_data['max_price'])
            
            if validated_data.get('is_featured'):
                query = query.filter_by(is_featured=True)
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            total = query.distinct().count()
            hotels = query.distinct().offset((page - 1) * per_page).limit(per_page).all()
            
            hotels_data = []
            for hotel in hotels:
                hotel_dict = hotel.to_dict()
                hotel_dict['images'] = [img.to_dict() for img in hotel.images]
                hotels_data.append(hotel_dict)
            
            return paginated_response(hotels_data, page, per_page, total)
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            return error_response(f'Lỗi tìm kiếm nâng cao: {str(e)}', 500)
    
    @staticmethod
    def get_suggestions():
        try:
            query_text = request.args.get('q', '')
            
            if not query_text:
                return success_response(data={'suggestions': []})
            
            cities = db.session.query(Hotel.city).filter(
                Hotel.city.ilike(f'%{query_text}%'),
                Hotel.status == 'active'
            ).distinct().limit(5).all()
            
            hotels = Hotel.query.filter(
                Hotel.hotel_name.ilike(f'%{query_text}%'),
                Hotel.status == 'active'
            ).limit(5).all()
            
            suggestions = []
            for city in cities:
                suggestions.append({'type': 'city', 'value': city[0]})
            
            for hotel in hotels:
                suggestions.append({'type': 'hotel', 'value': hotel.hotel_name, 'id': hotel.hotel_id})
            
            return success_response(data={'suggestions': suggestions})
            
        except Exception as e:
            return error_response(f'Lỗi lấy gợi ý: {str(e)}', 500)
    
    @staticmethod
    def get_search_history():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            query = SearchHistory.query.filter_by(user_id=session['user_id']).order_by(SearchHistory.search_date.desc())
            
            total = query.count()
            history = query.offset((page - 1) * per_page).limit(per_page).all()
            
            history_data = [h.to_dict() for h in history]
            
            return paginated_response(history_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Lỗi lấy lịch sử tìm kiếm: {str(e)}', 500)
    
    @staticmethod
    def delete_search_history(search_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            history = SearchHistory.query.filter_by(
                search_id=search_id,
                user_id=session['user_id']
            ).first()
            
            if not history:
                return error_response('Không tìm thấy lịch sử tìm kiếm', 404)
            
            db.session.delete(history)
            db.session.commit()
            
            return success_response(message='Xóa lịch sử tìm kiếm thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa lịch sử tìm kiếm thất bại: {str(e)}', 500)
    
    @staticmethod
    def check_availability():
        try:
            data = SearchController._get_request_data()
            
            required_fields = ['check_in', 'check_out']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = CheckAvailabilitySchema()
            validated_data = schema.load(data)
            
            check_in = validated_data['check_in']
            check_out = validated_data['check_out']
            
            if check_in >= check_out:
                return error_response('Ngày check-out phải sau ngày check-in', 400)
            
            query = Room.query.filter_by(status='available')
            
            if validated_data.get('hotel_id'):
                query = query.filter_by(hotel_id=validated_data['hotel_id'])
            
            if validated_data.get('room_type_id'):
                query = query.filter_by(room_type_id=validated_data['room_type_id'])
            
            if validated_data.get('num_guests'):
                query = query.filter(Room.max_guests >= validated_data['num_guests'])
            
            available_rooms = []
            for room in query.all():
                booked = db.session.query(func.sum(BookingDetail.quantity)).filter(
                    BookingDetail.room_id == room.room_id,
                    BookingDetail.booking.has(
                        and_(
                            BookingDetail.check_in_date < check_out,
                            BookingDetail.check_out_date > check_in,
                            or_(
                                BookingDetail.booking.has(status='confirmed'),
                                BookingDetail.booking.has(status='checked_in')
                            )
                        )
                    )
                ).scalar() or 0
                
                available_quantity = room.quantity - booked
                
                if available_quantity > 0:
                    room_dict = room.to_dict()
                    room_dict['available_quantity'] = int(available_quantity)
                    room_dict['hotel'] = room.hotel.to_dict() if room.hotel else None
                    room_dict['images'] = [img.to_dict() for img in room.images]
                    available_rooms.append(room_dict)
            
            return success_response(data={'available_rooms': available_rooms})
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            return error_response(f'Lỗi kiểm tra phòng trống: {str(e)}', 500)