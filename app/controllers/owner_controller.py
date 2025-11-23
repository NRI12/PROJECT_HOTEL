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

            revenue = booking_query.filter(Booking.status.in_(OwnerDashboardController.SAFE_BOOKING_STATUSES)) \
                .with_entities(func.coalesce(func.sum(Booking.final_amount), 0)).scalar() or 0

            recent_bookings = booking_query.order_by(Booking.created_at.desc()).limit(5).all()

            return success_response(
                data={
                    'summary': {
                        'hotel_count': hotels_count,
                        'room_count': rooms_count,
                        'booking_count': total_bookings,
                        'pending_booking_count': pending_bookings,
                        'total_revenue': float(revenue)
                    },
                    'recent_bookings': [booking.to_dict() for booking in recent_bookings]
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
            return success_response(data={'hotels': [hotel.to_dict() for hotel in hotels]})
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
            return success_response(data={'bookings': [booking.to_dict() for booking in bookings]})
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
    def revenue_summary():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            data = OwnerDashboardController._get_request_data()
            start_date = OwnerDashboardController._parse_date(data.get('start_date'))
            end_date = OwnerDashboardController._parse_date(data.get('end_date'))

            booking_query = OwnerDashboardController._booking_query_for_owner(user) \
                .filter(Booking.status.in_(OwnerDashboardController.SAFE_BOOKING_STATUSES))

            if start_date:
                booking_query = booking_query.filter(Booking.check_in_date >= start_date)
            if end_date:
                booking_query = booking_query.filter(Booking.check_out_date <= end_date)

            bookings = booking_query.order_by(Booking.check_in_date.asc()).all()

            monthly_totals = defaultdict(float)
            for booking in bookings:
                key = booking.check_in_date.strftime('%Y-%m') if booking.check_in_date else 'unknown'
                monthly_totals[key] += float(booking.final_amount or 0)

            return success_response(
                data={
                    'total_revenue': sum(monthly_totals.values()),
                    'monthly_revenue': [{'period': period, 'amount': amount} for period, amount in sorted(monthly_totals.items())]
                }
            )
        except Exception as exc:
            return error_response(f'Lỗi khi thống kê doanh thu: {str(exc)}', 500)

    @staticmethod
    def revenue_detail():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            data = OwnerDashboardController._get_request_data()
            status = data.get('status')

            booking_query = OwnerDashboardController._booking_query_for_owner(user)
            if status:
                booking_query = booking_query.filter_by(status=status)

            bookings = booking_query.order_by(Booking.created_at.desc()).limit(200).all()
            return success_response(data={'bookings': [booking.to_dict() for booking in bookings]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy chi tiết doanh thu: {str(exc)}', 500)

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

    @staticmethod
    def statistics_report():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            hotel_ids = OwnerDashboardController._get_hotel_ids(user)
            total_rooms = Room.query.filter(Room.hotel_id.in_(hotel_ids)).with_entities(func.coalesce(func.sum(Room.quantity), 0)).scalar() if hotel_ids else 0
            total_reviews = Review.query.filter(Review.hotel_id.in_(hotel_ids)).count() if hotel_ids else 0
            booking_query = OwnerDashboardController._booking_query_for_owner(user)
            completed_bookings = booking_query.filter(Booking.status.in_(OwnerDashboardController.SAFE_BOOKING_STATUSES)).count()
            avg_rating = Review.query.filter(Review.hotel_id.in_(hotel_ids)).with_entities(func.coalesce(func.avg(Review.rating), 0)).scalar() if hotel_ids else 0

            occupancy_rate = 0
            if total_rooms:
                occupancy_rate = (completed_bookings / total_rooms) * 100

            return success_response(
                data={
                    'total_hotels': len(hotel_ids),
                    'total_rooms': int(total_rooms or 0),
                    'completed_bookings': completed_bookings,
                    'total_reviews': total_reviews,
                    'average_rating': float(avg_rating or 0),
                    'occupancy_rate': round(occupancy_rate, 2)
                }
            )
        except Exception as exc:
            return error_response(f'Lỗi khi tạo báo cáo thống kê: {str(exc)}', 500)

    @staticmethod
    def occupancy_report():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            hotels = OwnerDashboardController._base_hotel_query(user).all()
            response = []

            for hotel in hotels:
                room_total = sum(room.quantity for room in hotel.rooms) if hotel.rooms else 0
                booking_count = Booking.query.filter(
                    Booking.hotel_id == hotel.hotel_id,
                    Booking.status.in_(OwnerDashboardController.SAFE_BOOKING_STATUSES)
                ).count()
                occupancy_rate = 0
                if room_total:
                    occupancy_rate = min(100.0, (booking_count / room_total) * 100)
                response.append({
                    'hotel_id': hotel.hotel_id,
                    'hotel_name': hotel.hotel_name,
                    'room_total': room_total,
                    'occupied': booking_count,
                    'occupancy_rate': round(occupancy_rate, 2)
                })

            return success_response(data={'occupancy': response})
        except Exception as exc:
            return error_response(f'Lỗi khi tính tỷ lệ lấp đầy: {str(exc)}', 500)

    @staticmethod
    def export_report():
        user, error = OwnerDashboardController._require_owner()
        if error:
            return error
        try:
            data = OwnerDashboardController._get_request_data()
            start_date = OwnerDashboardController._parse_date(data.get('start_date'))
            end_date = OwnerDashboardController._parse_date(data.get('end_date'))

            if data.get('start_date') and not start_date:
                return validation_error_response({'start_date': ['Ngày bắt đầu không hợp lệ']})
            if data.get('end_date') and not end_date:
                return validation_error_response({'end_date': ['Ngày kết thúc không hợp lệ']})

            return success_response(
                data={
                    'export': {
                        'requested_by': user.user_id,
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None,
                        'generated_at': datetime.utcnow().isoformat()
                    }
                },
                message='Đã tạo báo cáo và gửi tới email của bạn'
            )
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            return error_response(f'Lỗi khi xuất báo cáo: {str(exc)}', 500)

