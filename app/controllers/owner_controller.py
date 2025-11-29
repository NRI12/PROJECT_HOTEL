from datetime import datetime
from collections import defaultdict
from flask import request, session
from marshmallow import ValidationError
from sqlalchemy import func
from app import db
from app.models.booking import Booking
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.review import Review
from app.models.user import User
from app.models.promotion import Promotion
from app.utils.response import success_response, error_response, validation_error_response


class OwnerDashboardController:
    SAFE_BOOKING_STATUSES = ('confirmed', 'checked_in', 'checked_out')

    @staticmethod
    def _get_request_data():
        data = {}
        if request.args:
            data.update(request.args.to_dict(flat=True))
        if request.form:
            form_data = dict(request.form)
            for key, value in form_data.items():
                if isinstance(value, list) and len(value) == 1:
                    form_data[key] = value[0]
            data.update(form_data)
        elif request.is_json:
            payload = request.get_json() or {}
            if isinstance(payload, dict):
                data.update(payload)
        return data

    @staticmethod
    def _require_owner():
        if 'user_id' not in session:
            return None, error_response('Chưa đăng nhập', 401)

        user = User.query.get(session['user_id'])
        if not user or user.role.role_name not in ['hotel_owner', 'admin']:
            return None, error_response('Không có quyền truy cập', 403)
        return user, None

    @staticmethod
    def _base_hotel_query(user):
        query = Hotel.query
        if user.role.role_name != 'admin':
            query = query.filter_by(owner_id=user.user_id)
        return query

    @staticmethod
    def _get_hotel_ids(user):
        return [hotel.hotel_id for hotel in OwnerDashboardController._base_hotel_query(user).all()]

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _booking_query_for_owner(user):
        hotel_ids = OwnerDashboardController._get_hotel_ids(user)
        if not hotel_ids:
            return Booking.query.filter(False)
        return Booking.query.filter(Booking.hotel_id.in_(hotel_ids))

    @staticmethod
    def dashboard_overview():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            hotel_ids = OwnerDashboardController._get_hotel_ids(user)
            hotels_count = len(hotel_ids)
            rooms_count = Room.query.filter(Room.hotel_id.in_(hotel_ids)).count() if hotel_ids else 0

            booking_query = OwnerDashboardController._booking_query_for_owner(user)
            total_bookings = booking_query.count()
            pending_bookings = booking_query.filter_by(status='pending').count()

            revenue = booking_query.filter(Booking.status == 'checked_out') \
                .with_entities(func.coalesce(func.sum(Booking.final_amount), 0)).scalar() or 0

            recent_bookings = booking_query.order_by(Booking.created_at.desc()).limit(5).all()

            # Build bookings data with hotel and user info
            bookings_data = []
            for booking in recent_bookings:
                booking_dict = booking.to_dict()
                booking_dict['hotel'] = booking.hotel.to_dict() if booking.hotel else None
                booking_dict['user'] = booking.user.to_dict() if booking.user else None
                bookings_data.append(booking_dict)

            return success_response(
                data={
                    'summary': {
                        'hotel_count': hotels_count,
                        'room_count': rooms_count,
                        'booking_count': total_bookings,
                        'pending_booking_count': pending_bookings,
                        'total_revenue': float(revenue)
                    },
                    'recent_bookings': bookings_data
                }
            )
        except Exception as exc:
            return error_response(f'Lỗi khi lấy thống kê tổng quan: {str(exc)}', 500)

    @staticmethod
    def my_hotels():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            hotels = OwnerDashboardController._base_hotel_query(user).order_by(Hotel.created_at.desc()).all()
            hotels_data = []
            for hotel in hotels:
                hotel_dict = hotel.to_dict()
                # Include images
                hotel_dict['images'] = [img.to_dict() for img in hotel.images] if hotel.images else []
                hotels_data.append(hotel_dict)
            return success_response(data={'hotels': hotels_data})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách khách sạn: {str(exc)}', 500)

    @staticmethod
    def hotel_bookings():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            data = OwnerDashboardController._get_request_data()
            status = data.get('status')
            booking_query = OwnerDashboardController._booking_query_for_owner(user)
            if status:
                booking_query = booking_query.filter_by(status=status)
            bookings = booking_query.order_by(Booking.created_at.desc()).limit(100).all()
            
            # Build bookings data with hotel and user info
            bookings_data = []
            for booking in bookings:
                booking_dict = booking.to_dict()
                booking_dict['hotel'] = booking.hotel.to_dict() if booking.hotel else None
                booking_dict['user'] = booking.user.to_dict() if booking.user else None
                bookings_data.append(booking_dict)
            
            return success_response(data={'bookings': bookings_data})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy booking: {str(exc)}', 500)

    # INSTANT CONFIRM - No longer need pending bookings function
    # @staticmethod
    # def pending_bookings():
    #     user, error = OwnerDashboardController._require_owner()
    #     if error:
    #         return error
    #     try:
    #         booking_query = OwnerDashboardController._booking_query_for_owner(user).filter_by(status='pending')
    #         bookings = booking_query.order_by(Booking.created_at.asc()).all()
    #         return success_response(data={'bookings': [booking.to_dict() for booking in bookings]})
    #     except Exception as exc:
    #         return error_response(f'Lỗi khi lấy booking chờ xác nhận: {str(exc)}', 500)


    @staticmethod
    def room_status():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            hotel_ids = OwnerDashboardController._get_hotel_ids(user)
            rooms = Room.query.filter(Room.hotel_id.in_(hotel_ids)).order_by(Room.hotel_id, Room.room_name).all() if hotel_ids else []
            return success_response(data={'rooms': [room.to_dict() for room in rooms]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy trạng thái phòng: {str(exc)}', 500)

    @staticmethod
    def owner_rooms():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            data = OwnerDashboardController._get_request_data()
            status = data.get('status')
            hotel_id = data.get('hotel_id', type=int) if hasattr(data.get('hotel_id'), '__int__') else None
            
            # Get hotel IDs owned by this user
            hotel_ids = OwnerDashboardController._get_hotel_ids(user)
            
            if not hotel_ids:
                return success_response(data=[])
            
            # Build query filtering by owner's hotels
            query = Room.query.filter(Room.hotel_id.in_(hotel_ids))
            
            # Apply additional filters
            if hotel_id:
                query = query.filter_by(hotel_id=hotel_id)
            
            if status:
                query = query.filter_by(status=status)
            
            # Get rooms with relationships
            rooms = query.order_by(Room.hotel_id, Room.room_name).all()
            
            # Build response with related data
            rooms_data = []
            for room in rooms:
                room_dict = room.to_dict()
                room_dict['hotel'] = room.hotel.to_dict() if room.hotel else None
                room_dict['room_type'] = room.room_type.to_dict() if room.room_type else None
                room_dict['images'] = [img.to_dict() for img in room.images]
                rooms_data.append(room_dict)
            
            return success_response(data=rooms_data)
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách phòng: {str(exc)}', 500)

    @staticmethod
    def owner_promotions():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            hotel_ids = OwnerDashboardController._get_hotel_ids(user)
            
            if not hotel_ids:
                return success_response(data={'promotions': []})
            
            # Get promotions for owner's hotels
            promotions = Promotion.query.filter(
                (Promotion.hotel_id.in_(hotel_ids)) | (Promotion.hotel_id == None)
            ).order_by(Promotion.created_at.desc()).all()
            
            # Build response with hotel and room info
            promotions_data = []
            for promo in promotions:
                promo_dict = promo.to_dict()
                promo_dict['hotel'] = promo.hotel.to_dict() if promo.hotel else None
                promo_dict['room'] = promo.room.to_dict() if promo.room else None
                promotions_data.append(promo_dict)
            
            return success_response(data={'promotions': promotions_data})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách khuyến mãi: {str(exc)}', 500)

    @staticmethod
    def hotel_reviews():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            data = OwnerDashboardController._get_request_data()
            status = data.get('status', 'active')

            hotel_ids = OwnerDashboardController._get_hotel_ids(user)
            review_query = Review.query.filter(Review.hotel_id.in_(hotel_ids)) if hotel_ids else Review.query.filter(False)
            if status:
                review_query = review_query.filter_by(status=status)
            reviews = review_query.order_by(Review.created_at.desc()).limit(200).all()
            return success_response(data={'reviews': [review.to_dict() for review in reviews]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy đánh giá: {str(exc)}', 500)



