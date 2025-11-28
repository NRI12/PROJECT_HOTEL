from flask import request, session
from app import db
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.booking_detail import BookingDetail
from app.models.search_history import SearchHistory
from app.models.user import User
from app.models.amenity import Amenity
from app.models.cancellation_policy import CancellationPolicy
from app.models.promotion import Promotion
from app.schemas.search_schema import SearchSchema, AdvancedSearchSchema, CheckAvailabilitySchema
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from datetime import datetime, date
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload

class SearchController:
    
    @staticmethod
    def _get_request_data():
        data = {}
        
        # Ưu tiên GET params từ URL
        if request.args:
            data = {}
            for key in request.args.keys():
                values = request.args.getlist(key)
                if len(values) > 1:
                    data[key] = values
                else:
                    data[key] = values[0]
        elif request.form:
            data = dict(request.form)
            for key, value in data.items():
                if isinstance(value, list) and len(value) == 1:
                    data[key] = value[0]
        elif request.is_json:
            data = request.get_json() or {}
        
        # Chuẩn hóa tên field để tương thích
        if 'city' in data and 'destination' not in data:
            data['destination'] = data['city']
        if 'checkin' in data and 'check_in' not in data:
            data['check_in'] = data['checkin']
        if 'checkout' in data and 'check_out' not in data:
            data['check_out'] = data['checkout']
        if 'guests' in data and 'num_guests' not in data:
            # Xử lý format "2 người" -> 2
            guests_str = data['guests']
            if isinstance(guests_str, str):
                data['num_guests'] = guests_str.split()[0] if guests_str else '2'
            else:
                data['num_guests'] = guests_str
        
        # Chuẩn hóa danh sách hạng sao
        star_raw = data.get('star_rating')
        if star_raw:
            star_values = star_raw if isinstance(star_raw, list) else [star_raw]
            star_ints = []
            for value in star_values:
                try:
                    star_ints.append(int(value))
                except (TypeError, ValueError):
                    continue
            if star_ints:
                data['star_ratings'] = star_ints
                data['star_rating'] = min(star_ints)
        
        # Chuẩn hóa danh sách tiện nghi
        amenity_raw = data.get('amenity')
        if amenity_raw:
            amenity_values = amenity_raw if isinstance(amenity_raw, list) else [amenity_raw]
            amenity_ids = []
            for value in amenity_values:
                try:
                    amenity_ids.append(int(value))
                except (TypeError, ValueError):
                    continue
            data['amenity_ids'] = amenity_ids
            data.pop('amenity', None)
        
        # Chuẩn hóa boolean
        def parse_bool(value):
            if isinstance(value, list):
                value = value[-1]
            if isinstance(value, str):
                return value.lower() in ('1', 'true', 'on', 'yes')
            return bool(value)
        
        for bool_field in ('free_cancel', 'has_promotion', 'is_featured'):
            if bool_field in data:
                data[bool_field] = parse_bool(data[bool_field])
        
        return data

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
                
                # Thêm thông tin giá, đánh giá cho template
                from app.models.review import Review
                min_price = db.session.query(func.min(Room.base_price))\
                    .filter(Room.hotel_id == hotel.hotel_id)\
                    .filter(Room.status == 'available')\
                    .scalar() or 1000000
                
                review_count = Review.query.filter_by(hotel_id=hotel.hotel_id, status='active').count()
                
                avg_rating = db.session.query(func.avg(Review.rating))\
                    .filter_by(hotel_id=hotel.hotel_id, status='active')\
                    .scalar() or 4.0
                
                hotel_dict['min_price'] = int(min_price)
                hotel_dict['review_count'] = review_count
                hotel_dict['avg_rating'] = float(avg_rating) if avg_rating else 4.0
                
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
    
    @staticmethod
    def search_for_web():
        try:
            data = SearchController._get_request_data()
            
            from app.schemas.search_schema import SearchSchema
            from marshmallow import ValidationError
            
            try:
                schema = SearchSchema()
                validated_data = schema.load(data)
            except ValidationError as e:
                # Nếu validation fail, vẫn tiếp tục với data gốc
                validated_data = data
            
            # Query khách sạn active
            query = Hotel.query.filter_by(status='active')
            
            # Filter theo destination
            if validated_data.get('destination'):
                destination = validated_data['destination']
                query = query.filter(
                    or_(
                        Hotel.city.ilike(f'%{destination}%'),
                        Hotel.address.ilike(f'%{destination}%'),
                        Hotel.hotel_name.ilike(f'%{destination}%')
                    )
                )
            
            # Filter theo giá (cần join với Room)
            if validated_data.get('min_price') or validated_data.get('max_price'):
                query = query.join(Room, Room.hotel_id == Hotel.hotel_id)
                
                if validated_data.get('min_price'):
                    query = query.filter(Room.base_price >= validated_data['min_price'])
                
                if validated_data.get('max_price'):
                    query = query.filter(Room.base_price <= validated_data['max_price'])
            
            # Filter theo star rating
            star_filters = validated_data.get('star_ratings') or []
            if star_filters:
                min_star = min(star_filters)
                query = query.filter(Hotel.star_rating >= min_star)
            elif validated_data.get('star_rating'):
                query = query.filter(Hotel.star_rating >= validated_data['star_rating'])
            
            # Filter tiện nghi
            amenity_filters = validated_data.get('amenity_ids')
            if amenity_filters:
                for amenity_id in amenity_filters:
                    query = query.filter(Hotel.amenities.any(Amenity.amenity_id == amenity_id))
            
            # Filter featured
            if validated_data.get('is_featured'):
                query = query.filter(Hotel.is_featured.is_(True))
            
            # Filter hủy miễn phí
            if validated_data.get('free_cancel'):
                query = query.filter(
                    Hotel.cancellation_policies.any(CancellationPolicy.refund_percentage == 100.00)
                )
            
            # Filter khuyến mãi đang chạy
            if validated_data.get('has_promotion'):
                now = datetime.utcnow()
                query = query.filter(
                    Hotel.promotions.any(
                        and_(
                            Promotion.is_active.is_(True),
                            Promotion.start_date <= now,
                            Promotion.end_date >= now
                        )
                    )
                )
            
            # Phân trang
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # Đếm tổng và lấy dữ liệu (distinct để tránh duplicate khi join)
            total = query.distinct().count()
            hotels = query.options(
                joinedload(Hotel.images),
                joinedload(Hotel.amenities)
            ).distinct().offset((page - 1) * per_page).limit(per_page).all()
            
            # Build response data
            hotels_data = []
            for hotel in hotels:
                # Tính giá thấp nhất
                from app.models.review import Review
                min_price = db.session.query(func.min(Room.base_price))\
                    .filter(Room.hotel_id == hotel.hotel_id)\
                    .filter(Room.status == 'available')\
                    .scalar() or 1000000
                
                # Tính rating trung bình
                review_count = Review.query.filter_by(
                    hotel_id=hotel.hotel_id, 
                    status='active'
                ).count()
                
                avg_rating = db.session.query(func.avg(Review.rating))\
                    .filter_by(hotel_id=hotel.hotel_id, status='active')\
                    .scalar()
                
                # Kiểm tra có chính sách hủy miễn phí không (refund_percentage = 100%)
                from app.models.cancellation_policy import CancellationPolicy
                from app.models.promotion import Promotion
                has_free_cancellation = CancellationPolicy.query.filter_by(
                    hotel_id=hotel.hotel_id
                ).filter(
                    CancellationPolicy.refund_percentage == 100.00
                ).first() is not None
                
                # Kiểm tra có promotion đang active không
                has_active_promotion = Promotion.query.filter(
                    Promotion.hotel_id == hotel.hotel_id,
                    Promotion.start_date <= datetime.utcnow(),
                    Promotion.end_date >= datetime.utcnow(),
                    Promotion.is_active == True
                ).first() is not None
                
                hotels_data.append({
                    'hotel': hotel,
                    'min_price': int(min_price),
                    'review_count': review_count,
                    'avg_rating': float(avg_rating) if avg_rating else 4.0,
                    'has_free_cancellation': has_free_cancellation,
                    'has_active_promotion': has_active_promotion
                })
            
            # Lưu lịch sử tìm kiếm (nếu user đã login)
            if 'user_id' in session and validated_data.get('destination'):
                try:
                    history = SearchHistory(
                        user_id=session['user_id'],
                        destination=validated_data['destination'],
                        check_in_date=validated_data.get('check_in'),
                        check_out_date=validated_data.get('check_out'),
                        num_guests=validated_data.get('num_guests')
                    )
                    db.session.add(history)
                    db.session.commit()
                except:
                    db.session.rollback()
            
            # Tính total_pages
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1
            
            # Return dict thay vì response object
            return {
                'data': hotels_data,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return {
                'data': [],
                'total': 0,
                'page': 1,
                'per_page': 10,
                'total_pages': 1
            }
        try:
            data = SearchController._get_request_data()
            
            from app.schemas.search_schema import SearchSchema
            from marshmallow import ValidationError
            
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
                from app.models.review import Review
                min_price = db.session.query(func.min(Room.base_price))\
                    .filter(Room.hotel_id == hotel.hotel_id)\
                    .filter(Room.status == 'available')\
                    .scalar() or 1000000
                
                review_count = Review.query.filter_by(hotel_id=hotel.hotel_id, status='active').count()
                
                avg_rating = db.session.query(func.avg(Review.rating))\
                    .filter_by(hotel_id=hotel.hotel_id, status='active')\
                    .scalar() or 4.0
                
                hotels_data.append({
                    'hotel': hotel,
                    'min_price': int(min_price),
                    'review_count': review_count,
                    'avg_rating': float(avg_rating) if avg_rating else 4.0
                })
            
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
            
            total_pages = (total + per_page - 1) // per_page
            return {
                'hotels': hotels_data,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
            
        except ValidationError as e:
            print(f'Validation error: {e.messages}')
            return {'hotels': [], 'total': 0, 'page': 1, 'per_page': 10, 'total_pages': 1}
        except Exception as e:
            print(f'Lỗi tìm kiếm: {str(e)}')
            return {'hotels': [], 'total': 0, 'page': 1, 'per_page': 10, 'total_pages': 1}