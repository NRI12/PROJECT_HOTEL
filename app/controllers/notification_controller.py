from flask import request, session
from marshmallow import ValidationError

from app import db
from app.models.notification import Notification
from app.schemas.notification_schema import NotificationReadSchema
from app.utils.response import success_response, error_response, validation_error_response


class NotificationController:
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
    def _require_login():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        return None

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
        return None

    @staticmethod
    def list_notifications():
        auth_error = NotificationController._require_login()
        if auth_error:
            return auth_error
        try:
            data = NotificationController._get_request_data()
            query = Notification.query.filter_by(user_id=session['user_id'])

            notif_type = data.get('type')
            if notif_type:
                query = query.filter_by(type=notif_type)

            is_read_value = data.get('is_read')
            if is_read_value not in [None, '']:
                parsed = NotificationController._parse_bool(is_read_value)
                if parsed is None:
                    return error_response('Giá trị is_read không hợp lệ', 400)
                query = query.filter_by(is_read=parsed)

            notifications = query.order_by(Notification.created_at.desc()).all()
            notifications_data = [notification.to_dict() for notification in notifications]

            return success_response(
                data={'notifications': notifications_data},
                message='Lấy danh sách thông báo thành công'
            )
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách thông báo: {str(exc)}', 500)

    @staticmethod
    def list_unread_notifications():
        auth_error = NotificationController._require_login()
        if auth_error:
            return auth_error
        try:
            notifications = Notification.query.filter_by(
                user_id=session['user_id'],
                is_read=False
            ).order_by(Notification.created_at.desc()).all()

            notifications_data = [notification.to_dict() for notification in notifications]
            return success_response(
                data={'notifications': notifications_data},
                message='Lấy danh sách thông báo chưa đọc thành công'
            )
        except Exception as exc:
            return error_response(f'Lỗi khi lấy thông báo chưa đọc: {str(exc)}', 500)

    @staticmethod
    def get_notification(notification_id):
        auth_error = NotificationController._require_login()
        if auth_error:
            return auth_error
        try:
            notification = Notification.query.filter_by(
                notification_id=notification_id,
                user_id=session['user_id']
            ).first()
            if not notification:
                return error_response('Không tìm thấy thông báo', 404)

            return success_response(
                data={'notification': notification.to_dict()},
                message='Lấy chi tiết thông báo thành công'
            )
        except Exception as exc:
            return error_response(f'Lỗi khi lấy chi tiết thông báo: {str(exc)}', 500)

    @staticmethod
    def mark_as_read(notification_id):
        auth_error = NotificationController._require_login()
        if auth_error:
            return auth_error
        try:
            data = NotificationController._get_request_data()
            schema = NotificationReadSchema()
            payload = schema.load(data)

            notification = Notification.query.filter_by(
                notification_id=notification_id,
                user_id=session['user_id']
            ).first()
            if not notification:
                return error_response('Không tìm thấy thông báo', 404)

            notification.is_read = payload.get('is_read', True)
            db.session.commit()

            return success_response(
                data={'notification': notification.to_dict()},
                message='Đã cập nhật trạng thái thông báo'
            )
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Không thể cập nhật thông báo: {str(exc)}', 500)

    @staticmethod
    def mark_all_as_read():
        auth_error = NotificationController._require_login()
        if auth_error:
            return auth_error
        try:
            Notification.query.filter_by(
                user_id=session['user_id'],
                is_read=False
            ).update({'is_read': True})
            db.session.commit()

            return success_response(message='Đã đánh dấu tất cả thông báo là đã đọc')
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Không thể cập nhật toàn bộ thông báo: {str(exc)}', 500)

    @staticmethod
    def delete_notification(notification_id):
        auth_error = NotificationController._require_login()
        if auth_error:
            return auth_error
        try:
            notification = Notification.query.filter_by(
                notification_id=notification_id,
                user_id=session['user_id']
            ).first()
            if not notification:
                return error_response('Không tìm thấy thông báo để xóa', 404)

            db.session.delete(notification)
            db.session.commit()

            return success_response(message='Đã xóa thông báo')
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Không thể xóa thông báo: {str(exc)}', 500)

    @staticmethod
    def clear_notifications():
        auth_error = NotificationController._require_login()
        if auth_error:
            return auth_error
        try:
            Notification.query.filter_by(user_id=session['user_id']).delete(synchronize_session=False)
            db.session.commit()

            return success_response(message='Đã xóa toàn bộ thông báo')
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Không thể xóa toàn bộ thông báo: {str(exc)}', 500)

