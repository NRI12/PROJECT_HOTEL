from flask import Blueprint, render_template, redirect, url_for, flash, request

from app.controllers.admin_controller import AdminPanelController
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _extract_payload(result):
    try:
        return result[0].get_json()
    except Exception:
        return {}


def _render_template(result, template, **context):
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


def _redirect(endpoint, **extra):
    params = request.args.to_dict(flat=True)
    params.update(extra)
    return redirect(url_for(endpoint, **params))


@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def admin_dashboard():
    result = AdminPanelController.dashboard_overview()
    return _render_template(result, 'admin/dashboard.html')


@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def admin_users():
    result = AdminPanelController.list_users()
    return _render_template(result, 'admin/users.html')


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@role_required('admin')
def admin_user_detail(user_id):
    result = AdminPanelController.user_detail(user_id)
    return _render_template(result, 'admin/user_detail.html', user_id=user_id)


@admin_bp.route('/users/<int:user_id>/status', methods=['POST', 'PUT'])
@role_required('admin')
def admin_user_status(user_id):
    result = AdminPanelController.update_user_status(user_id)
    _flash_from_result(result, 'Đã cập nhật trạng thái người dùng', 'Cập nhật trạng thái thất bại')
    return _redirect('admin.admin_user_detail', user_id=user_id)


@admin_bp.route('/users/<int:user_id>/role', methods=['POST', 'PUT'])
@role_required('admin')
def admin_user_role(user_id):
    result = AdminPanelController.update_user_role(user_id)
    _flash_from_result(result, 'Đã cập nhật role người dùng', 'Cập nhật role thất bại')
    return _redirect('admin.admin_user_detail', user_id=user_id)


@admin_bp.route('/users/<int:user_id>', methods=['DELETE', 'POST'])
@role_required('admin')
def admin_user_delete(user_id):
    result = AdminPanelController.delete_user(user_id)
    _flash_from_result(result, 'Đã xóa người dùng', 'Xóa người dùng thất bại')
    return _redirect('admin.admin_users')


@admin_bp.route('/hotels', methods=['GET'])
@role_required('admin')
def admin_hotels():
    result = AdminPanelController.list_hotels()
    return _render_template(result, 'admin/hotels.html')


@admin_bp.route('/hotels/pending', methods=['GET'])
@role_required('admin')
def admin_hotels_pending():
    result = AdminPanelController.pending_hotels()
    return _render_template(result, 'admin/hotels_pending.html')


@admin_bp.route('/hotels/<int:hotel_id>/approve', methods=['POST', 'PUT'])
@role_required('admin')
def admin_hotels_approve(hotel_id):
    result = AdminPanelController.approve_hotel(hotel_id)
    _flash_from_result(result, 'Đã duyệt khách sạn', 'Duyệt khách sạn thất bại')
    return _redirect('admin.admin_hotels')


@admin_bp.route('/hotels/<int:hotel_id>/reject', methods=['POST', 'PUT'])
@role_required('admin')
def admin_hotels_reject(hotel_id):
    result = AdminPanelController.reject_hotel(hotel_id)
    _flash_from_result(result, 'Đã từ chối khách sạn', 'Từ chối khách sạn thất bại')
    return _redirect('admin.admin_hotels_pending')


@admin_bp.route('/hotels/<int:hotel_id>/suspend', methods=['POST', 'PUT'])
@role_required('admin')
def admin_hotels_suspend(hotel_id):
    result = AdminPanelController.suspend_hotel(hotel_id)
    _flash_from_result(result, 'Đã đình chỉ khách sạn', 'Đình chỉ khách sạn thất bại')
    return _redirect('admin.admin_hotels')


@admin_bp.route('/hotels/<int:hotel_id>/featured', methods=['POST', 'PUT'])
@role_required('admin')
def admin_hotels_featured(hotel_id):
    result = AdminPanelController.feature_hotel(hotel_id)
    _flash_from_result(result, 'Đã cập nhật nổi bật', 'Không thể cập nhật nổi bật')
    return _redirect('admin.admin_hotels')


@admin_bp.route('/bookings', methods=['GET'])
@role_required('admin')
def admin_bookings():
    result = AdminPanelController.list_bookings()
    return _render_template(result, 'admin/bookings.html')


@admin_bp.route('/bookings/statistics', methods=['GET'])
@role_required('admin')
def admin_booking_statistics():
    # Redirect to dashboard
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/payments', methods=['GET'])
@role_required('admin')
def admin_payments():
    result = AdminPanelController.list_payments()
    return _render_template(result, 'admin/payments.html')


@admin_bp.route('/reviews', methods=['GET'])
@role_required('admin')
def admin_reviews():
    result = AdminPanelController.list_reviews()
    return _render_template(result, 'admin/reviews.html')


@admin_bp.route('/reviews/<int:review_id>/hide', methods=['POST', 'PUT'])
@role_required('admin')
def admin_review_hide(review_id):
    result = AdminPanelController.hide_review(review_id)
    _flash_from_result(result, 'Đã ẩn đánh giá', 'Ẩn đánh giá thất bại')
    return _redirect('admin.admin_reviews')


@admin_bp.route('/reviews/<int:review_id>', methods=['DELETE', 'POST'])
@role_required('admin')
def admin_review_delete(review_id):
    result = AdminPanelController.delete_review(review_id)
    _flash_from_result(result, 'Đã xóa đánh giá', 'Xóa đánh giá thất bại')
    return _redirect('admin.admin_reviews')


@admin_bp.route('/statistics', methods=['GET'])
@role_required('admin')
def admin_statistics():
    # Redirect to dashboard - all statistics are now in dashboard
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/statistics/revenue', methods=['GET'])
@role_required('admin')
def admin_statistics_revenue():
    # Redirect to dashboard
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/statistics/users', methods=['GET'])
@role_required('admin')
def admin_statistics_users():
    # Redirect to dashboard
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/statistics/bookings', methods=['GET'])
@role_required('admin')
def admin_statistics_bookings():
    # Redirect to dashboard
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/reports/export', methods=['POST'])
@role_required('admin')
def admin_export_report():
    result = AdminPanelController.export_report()
    _flash_from_result(result, 'Đã tạo báo cáo hệ thống', 'Xuất báo cáo thất bại')
    return _redirect('admin.admin_statistics')


@admin_bp.route('/roles', methods=['GET'])
@role_required('admin')
def admin_roles():
    result = AdminPanelController.list_roles()
    return _render_template(result, 'admin/roles.html')


@admin_bp.route('/roles', methods=['POST'])
@role_required('admin')
def admin_roles_create():
    result = AdminPanelController.create_role()
    _flash_from_result(result, 'Đã tạo role', 'Tạo role thất bại')
    return _redirect('admin.admin_roles')


@admin_bp.route('/roles/<int:role_id>', methods=['PUT', 'POST'])
@role_required('admin')
def admin_roles_update(role_id):
    result = AdminPanelController.update_role(role_id)
    _flash_from_result(result, 'Đã cập nhật role', 'Cập nhật role thất bại')
    return _redirect('admin.admin_roles')


@admin_bp.route('/roles/<int:role_id>', methods=['DELETE', 'POST'])
@role_required('admin')
def admin_roles_delete(role_id):
    result = AdminPanelController.delete_role(role_id)
    _flash_from_result(result, 'Đã xóa role', 'Xóa role thất bại')
    return _redirect('admin.admin_roles')