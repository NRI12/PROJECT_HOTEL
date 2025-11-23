from flask import Blueprint, render_template, redirect, url_for, flash, request

from app.controllers.notification_controller import NotificationController

notification_bp = Blueprint('notification', __name__)


def _extract_payload(result):
    try:
        return result[0].get_json()
    except Exception:
        return {}


def _render_notification_template(result, template='notification/list.html', **context):
    payload = _extract_payload(result)
    error = payload.get('message') if result[1] >= 400 else None
    success = payload.get('message') if result[1] < 400 else None
    return render_template(template, result=result, error=error, success=success, **context)


def _flash_from_result(result, success_fallback, error_fallback):
    payload = _extract_payload(result)
    message = payload.get('message')
    if result[1] >= 400:
        flash(message or error_fallback, 'error')
    else:
        flash(message or success_fallback, 'success')


def _redirect_with_params(default_endpoint, **extra):
    params = request.args.to_dict(flat=True)
    params.update(extra)
    return redirect(url_for(default_endpoint, **params))


@notification_bp.route('/notification', methods=['GET'])
@notification_bp.route('/notification/', methods=['GET'])
def list_notifications():
    view = request.args.get('view', 'all')
    if view == 'unread':
        result = NotificationController.list_unread_notifications()
        return _render_notification_template(result, view_mode='unread')
    result = NotificationController.list_notifications()
    return _render_notification_template(result, view_mode='all')


@notification_bp.route('/notification/<int:notification_id>', methods=['GET'])
def notification_detail(notification_id):
    result = NotificationController.get_notification(notification_id)
    return _render_notification_template(
        result,
        template='notification/detail.html',
        notification_id=notification_id,
        back_url=request.args.get('next') or url_for('notification.list_notifications')
    )


@notification_bp.route('/api/notifications', methods=['GET'])
def list_notifications_api():
    result = NotificationController.list_notifications()
    return _render_notification_template(result, view_mode='all')


@notification_bp.route('/api/notifications/unread', methods=['GET'])
def list_unread_notifications_api():
    result = NotificationController.list_unread_notifications()
    return _render_notification_template(result, view_mode='unread')


@notification_bp.route('/api/notifications/<int:notification_id>', methods=['GET'])
def notification_detail_api(notification_id):
    result = NotificationController.get_notification(notification_id)
    return _render_notification_template(
        result,
        template='notification/detail.html',
        notification_id=notification_id,
        back_url=request.args.get('next') or url_for('notification.list_notifications_api')
    )


@notification_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE', 'POST'])
def delete_notification_api(notification_id):
    result = NotificationController.delete_notification(notification_id)
    _flash_from_result(result, 'Đã xóa thông báo', 'Xóa thông báo thất bại')
    return _redirect_with_params('notification.list_notifications_api')


@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST', 'PUT'])
def mark_notification_read_api(notification_id):
    result = NotificationController.mark_as_read(notification_id)
    _flash_from_result(result, 'Đã cập nhật thông báo', 'Không thể cập nhật thông báo')
    next_url = request.args.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('notification.notification_detail_api', notification_id=notification_id))


@notification_bp.route('/api/notifications/read-all', methods=['POST', 'PUT'])
def mark_all_notifications_read_api():
    result = NotificationController.mark_all_as_read()
    _flash_from_result(result, 'Đã đánh dấu toàn bộ là đã đọc', 'Không thể cập nhật')
    return _redirect_with_params('notification.list_notifications_api')


@notification_bp.route('/api/notifications/clear', methods=['POST', 'DELETE'])
def clear_notifications_api():
    result = NotificationController.clear_notifications()
    _flash_from_result(result, 'Đã xóa toàn bộ thông báo', 'Không thể xóa thông báo')
    return _redirect_with_params('notification.list_notifications_api')
