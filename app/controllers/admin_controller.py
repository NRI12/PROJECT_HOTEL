from datetime import datetime
from collections import defaultdict

from flask import request, session
from marshmallow import ValidationError
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.role import Role
from app.models.hotel import Hotel
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.review import Review
from app.utils.response import success_response, error_response, validation_error_response


class AdminPanelController:
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
    def _require_admin():
        if 'user_id' not in session:
            return None, error_response('Chưa đăng nhập', 401)

        user = User.query.get(session['user_id'])
        if not user or user.role.role_name != 'admin':
            return None, error_response('Không có quyền truy cập', 403)
        return user, None

    @staticmethod
    def _parse_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in ['true', '1', 'yes']:
                return True
            if lowered in ['false', '0', 'no']:
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        return None

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
    def dashboard_overview():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            total_hotels = Hotel.query.count()
            pending_hotels = Hotel.query.filter_by(status='pending').count()
            total_bookings = Booking.query.count()
            total_payments = Payment.query.count()
            total_revenue = Booking.query.filter(
                Booking.status.in_(AdminPanelController.SAFE_BOOKING_STATUSES)
            ).with_entities(func.coalesce(func.sum(Booking.final_amount), 0)).scalar() or 0

            recent_hotels = Hotel.query.order_by(Hotel.created_at.desc()).limit(5).all()
            recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

            return success_response(data={
                'summary': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'total_hotels': total_hotels,
                    'pending_hotels': pending_hotels,
                    'total_bookings': total_bookings,
                    'total_payments': total_payments,
                    'total_revenue': float(total_revenue)
                },
                'recent_hotels': [hotel.to_dict() for hotel in recent_hotels],
                'recent_users': [user.to_dict() for user in recent_users]
            })
        except Exception as exc:
            return error_response(f'Lỗi khi lấy dashboard: {str(exc)}', 500)

    @staticmethod
    def list_users():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            query = User.query.order_by(User.created_at.desc())

            role_id = data.get('role_id')
            if role_id:
                query = query.filter_by(role_id=role_id)

            is_active = data.get('is_active')
            if is_active not in [None, '']:
                parsed = AdminPanelController._parse_bool(is_active)
                if parsed is None:
                    return error_response('Giá trị is_active không hợp lệ', 400)
                query = query.filter_by(is_active=parsed)

            search = data.get('q')
            if search:
                like_pattern = f"%{search}%"
                query = query.filter(
                    (User.full_name.ilike(like_pattern)) |
                    (User.email.ilike(like_pattern))
                )

            users = query.limit(200).all()
            return success_response(data={'users': [user.to_dict() for user in users]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách người dùng: {str(exc)}', 500)

    @staticmethod
    def user_detail(user_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            user = User.query.get(user_id)
            if not user:
                return error_response('Không tìm thấy người dùng', 404)
            return success_response(data={'user': user.to_dict(include_sensitive=False)})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy chi tiết người dùng: {str(exc)}', 500)

    @staticmethod
    def update_user_status(user_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            status_value = data.get('is_active')
            parsed = AdminPanelController._parse_bool(status_value)
            if parsed is None:
                return validation_error_response({'is_active': ['Giá trị không hợp lệ']})

            user = User.query.get(user_id)
            if not user:
                return error_response('Không tìm thấy người dùng', 404)

            user.is_active = parsed
            db.session.commit()
            return success_response(data={'user': user.to_dict()}, message='Đã cập nhật trạng thái người dùng')
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi cập nhật trạng thái người dùng: {str(exc)}', 500)

    @staticmethod
    def update_user_role(user_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            role_id = data.get('role_id')
            if not role_id:
                return validation_error_response({'role_id': ['role_id là bắt buộc']})

            role = Role.query.get(role_id)
            if not role:
                return error_response('Không tìm thấy role', 404)

            user = User.query.get(user_id)
            if not user:
                return error_response('Không tìm thấy người dùng', 404)

            user.role_id = role.role_id
            db.session.commit()
            return success_response(data={'user': user.to_dict()}, message='Đã cập nhật role người dùng')
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi cập nhật role: {str(exc)}', 500)

    @staticmethod
    def delete_user(user_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            user = User.query.get(user_id)
            if not user:
                return error_response('Không tìm thấy người dùng', 404)

            db.session.delete(user)
            db.session.commit()
            return success_response(message='Đã xóa người dùng')
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi xóa người dùng: {str(exc)}', 500)

    @staticmethod
    def list_hotels():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            query = Hotel.query.order_by(Hotel.created_at.desc())
            status = data.get('status')
            if status:
                query = query.filter_by(status=status)
            hotels = query.limit(200).all()
            return success_response(data={'hotels': [hotel.to_dict() for hotel in hotels]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách khách sạn: {str(exc)}', 500)

    @staticmethod
    def pending_hotels():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            hotels = Hotel.query.filter_by(status='pending').order_by(Hotel.created_at.asc()).all()
            return success_response(data={'hotels': [hotel.to_dict() for hotel in hotels]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy khách sạn chờ duyệt: {str(exc)}', 500)

    @staticmethod
    def _update_hotel_status(hotel_id, status=None, featured=None):
        _, error = AdminPanelController._require_admin()
        if error:
            return None, error
        try:
            hotel = Hotel.query.get(hotel_id)
            if not hotel:
                return None, error_response('Không tìm thấy khách sạn', 404)

            if status:
                hotel.status = status
            if featured is not None:
                hotel.is_featured = featured

            db.session.commit()
            return hotel, None
        except Exception as exc:
            db.session.rollback()
            return None, error_response(f'Lỗi khi cập nhật khách sạn: {str(exc)}', 500)

    @staticmethod
    def approve_hotel(hotel_id):
        hotel, error = AdminPanelController._update_hotel_status(hotel_id, status='active')
        if error:
            return error
        return success_response(data={'hotel': hotel.to_dict()}, message='Đã duyệt khách sạn')

    @staticmethod
    def reject_hotel(hotel_id):
        hotel, error = AdminPanelController._update_hotel_status(hotel_id, status='rejected')
        if error:
            return error
        return success_response(data={'hotel': hotel.to_dict()}, message='Đã từ chối khách sạn')

    @staticmethod
    def suspend_hotel(hotel_id):
        hotel, error = AdminPanelController._update_hotel_status(hotel_id, status='suspended')
        if error:
            return error
        return success_response(data={'hotel': hotel.to_dict()}, message='Đã đình chỉ khách sạn')

    @staticmethod
    def feature_hotel(hotel_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            featured_value = data.get('is_featured')
            parsed = AdminPanelController._parse_bool(featured_value)
            if parsed is None:
                return validation_error_response({'is_featured': ['Giá trị không hợp lệ']})

            hotel = Hotel.query.get(hotel_id)
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)

            hotel.is_featured = parsed
            db.session.commit()
            return success_response(data={'hotel': hotel.to_dict()}, message='Đã cập nhật nổi bật')
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi cập nhật nổi bật: {str(exc)}', 500)

    @staticmethod
    def list_bookings():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            query = Booking.query.order_by(Booking.created_at.desc())
            status = data.get('status')
            if status:
                query = query.filter_by(status=status)
            bookings = query.limit(200).all()
            return success_response(data={'bookings': [booking.to_dict() for booking in bookings]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách booking: {str(exc)}', 500)

    @staticmethod
    def booking_statistics():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            total = Booking.query.count()
            by_status = Booking.query.with_entities(Booking.status, func.count(Booking.booking_id)) \
                .group_by(Booking.status).all()
            status_data = {status: count for status, count in by_status}

            revenue = Booking.query.filter(
                Booking.status.in_(AdminPanelController.SAFE_BOOKING_STATUSES)
            ).with_entities(func.coalesce(func.sum(Booking.final_amount), 0)).scalar() or 0

            recent = Booking.query.order_by(Booking.created_at.desc()).limit(20).all()

            return success_response(data={
                'total_bookings': total,
                'status_breakdown': status_data,
                'completed_revenue': float(revenue),
                'recent_bookings': [booking.to_dict() for booking in recent]
            })
        except Exception as exc:
            return error_response(f'Lỗi khi thống kê booking: {str(exc)}', 500)

    @staticmethod
    def list_payments():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            payments = Payment.query.order_by(Payment.created_at.desc()).limit(200).all()
            return success_response(data={'payments': [payment.to_dict() for payment in payments]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách thanh toán: {str(exc)}', 500)

    @staticmethod
    def list_reviews():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            query = Review.query.order_by(Review.created_at.desc())
            status = data.get('status')
            if status:
                query = query.filter_by(status=status)
            reviews = query.limit(200).all()
            return success_response(data={'reviews': [review.to_dict() for review in reviews]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy đánh giá: {str(exc)}', 500)

    @staticmethod
    def hide_review(review_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy đánh giá', 404)
            review.status = 'hidden'
            db.session.commit()
            return success_response(data={'review': review.to_dict()}, message='Đã ẩn đánh giá')
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi ẩn đánh giá: {str(exc)}', 500)

    @staticmethod
    def delete_review(review_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy đánh giá', 404)
            db.session.delete(review)
            db.session.commit()
            return success_response(message='Đã xóa đánh giá')
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi xóa đánh giá: {str(exc)}', 500)

    @staticmethod
    def system_statistics():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            total_users = User.query.count()
            total_hotels = Hotel.query.count()
            total_bookings = Booking.query.count()
            total_payments = Payment.query.count()
            total_reviews = Review.query.count()

            active_hotels = Hotel.query.filter_by(status='active').count()
            featured_hotels = Hotel.query.filter_by(is_featured=True).count()

            return success_response(data={
                'totals': {
                    'users': total_users,
                    'hotels': total_hotels,
                    'bookings': total_bookings,
                    'payments': total_payments,
                    'reviews': total_reviews
                },
                'hotels': {
                    'active': active_hotels,
                    'featured': featured_hotels
                }
            })
        except Exception as exc:
            return error_response(f'Lỗi khi thống kê hệ thống: {str(exc)}', 500)

    @staticmethod
    def revenue_statistics():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            bookings = Booking.query.filter(
                Booking.status.in_(AdminPanelController.SAFE_BOOKING_STATUSES)
            ).order_by(Booking.check_in_date.asc()).all()
            monthly = defaultdict(float)
            for booking in bookings:
                key = booking.check_in_date.strftime('%Y-%m') if booking.check_in_date else 'unknown'
                monthly[key] += float(booking.final_amount or 0)
            return success_response(data={
                'monthly_revenue': [{'period': period, 'amount': amount} for period, amount in sorted(monthly.items())],
                'total_revenue': sum(monthly.values())
            })
        except Exception as exc:
            return error_response(f'Lỗi khi thống kê doanh thu hệ thống: {str(exc)}', 500)

    @staticmethod
    def user_statistics():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            by_role = User.query.with_entities(User.role_id, func.count(User.user_id)).group_by(User.role_id).all()
            role_map = {role.role_id: role.role_name for role in Role.query.all()}
            stats = [{'role_id': role_id, 'role_name': role_map.get(role_id, 'unknown'), 'count': count} for role_id, count in by_role]
            active = User.query.filter_by(is_active=True).count()
            inactive = User.query.filter_by(is_active=False).count()
            return success_response(data={
                'by_role': stats,
                'active_users': active,
                'inactive_users': inactive
            })
        except Exception as exc:
            return error_response(f'Lỗi khi thống kê người dùng: {str(exc)}', 500)

    @staticmethod
    def booking_statistics_detail():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            by_status = Booking.query.with_entities(Booking.status, func.count(Booking.booking_id)).group_by(Booking.status).all()
            by_payment = Booking.query.with_entities(Booking.payment_status, func.count(Booking.booking_id)).group_by(Booking.payment_status).all()
            return success_response(data={
                'by_status': {status: count for status, count in by_status},
                'by_payment_status': {status: count for status, count in by_payment}
            })
        except Exception as exc:
            return error_response(f'Lỗi khi thống kê booking chi tiết: {str(exc)}', 500)

    @staticmethod
    def export_report():
        user, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            start_date = AdminPanelController._parse_date(data.get('start_date'))
            end_date = AdminPanelController._parse_date(data.get('end_date'))

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
                message='Đã tạo báo cáo hệ thống'
            )
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            return error_response(f'Lỗi khi xuất báo cáo: {str(exc)}', 500)

    @staticmethod
    def list_roles():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            roles = Role.query.order_by(Role.created_at.desc()).all()
            return success_response(data={'roles': [role.to_dict() for role in roles]})
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách role: {str(exc)}', 500)

    @staticmethod
    def create_role():
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            data = AdminPanelController._get_request_data()
            role_name = data.get('role_name')
            if not role_name:
                return validation_error_response({'role_name': ['role_name là bắt buộc']})

            role = Role(role_name=role_name, description=data.get('description'))
            db.session.add(role)
            db.session.commit()
            return success_response(data={'role': role.to_dict()}, message='Đã tạo role', status_code=201)
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi tạo role: {str(exc)}', 500)

    @staticmethod
    def update_role(role_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            role = Role.query.get(role_id)
            if not role:
                return error_response('Không tìm thấy role', 404)
            data = AdminPanelController._get_request_data()
            if 'role_name' in data and data['role_name']:
                role.role_name = data['role_name']
            if 'description' in data:
                role.description = data['description']
            db.session.commit()
            return success_response(data={'role': role.to_dict()}, message='Đã cập nhật role')
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi cập nhật role: {str(exc)}', 500)

    @staticmethod
    def delete_role(role_id):
        _, error = AdminPanelController._require_admin()
        if error:
            return error
        try:
            role = Role.query.get(role_id)
            if not role:
                return error_response('Không tìm thấy role', 404)
            db.session.delete(role)
            db.session.commit()
            return success_response(message='Đã xóa role')
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Lỗi khi xóa role: {str(exc)}', 500)

