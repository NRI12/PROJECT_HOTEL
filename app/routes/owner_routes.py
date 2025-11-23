from flask import Blueprint, render_template, redirect, url_for, flash, request

from app.controllers.owner_controller import OwnerDashboardController

owner_bp = Blueprint('owner', __name__, url_prefix='/api/owner')


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


def _redirect_with_params(endpoint='owner.dashboard'):
    params = request.args.to_dict(flat=True)
    return redirect(url_for(endpoint, **params))


@owner_bp.route('/dashboard', methods=['GET'])
def dashboard():
    result = OwnerDashboardController.dashboard_overview()
    return _render_template(result, 'owner/dashboard.html')


@owner_bp.route('/hotels', methods=['GET'])
def my_hotels():
    result = OwnerDashboardController.my_hotels()
    return _render_template(result, 'owner/hotels.html')


@owner_bp.route('/bookings', methods=['GET'])
def owner_bookings():
    result = OwnerDashboardController.hotel_bookings()
    return _render_template(result, 'owner/bookings.html')


# INSTANT CONFIRM - No longer need pending bookings page
# @owner_bp.route('/bookings/pending', methods=['GET'])
# def pending_bookings():
#     result = OwnerDashboardController.pending_bookings()
#     return _render_template(result, 'owner/bookings_pending.html')


@owner_bp.route('/revenue', methods=['GET'])
def revenue_summary():
    result = OwnerDashboardController.revenue_summary()
    return _render_template(result, 'owner/revenue.html')


@owner_bp.route('/revenue/detail', methods=['GET'])
def revenue_detail():
    result = OwnerDashboardController.revenue_detail()
    return _render_template(result, 'owner/revenue_detail.html')


@owner_bp.route('/rooms/status', methods=['GET'])
def rooms_status():
    result = OwnerDashboardController.room_status()
    return _render_template(result, 'owner/rooms_status.html')


@owner_bp.route('/reviews', methods=['GET'])
def owner_reviews():
    result = OwnerDashboardController.hotel_reviews()
    return _render_template(result, 'owner/reviews.html')


@owner_bp.route('/statistics', methods=['GET'])
def statistics_report():
    result = OwnerDashboardController.statistics_report()
    return _render_template(result, 'owner/statistics.html')


@owner_bp.route('/occupancy', methods=['GET'])
def occupancy_report():
    result = OwnerDashboardController.occupancy_report()
    return _render_template(result, 'owner/occupancy.html')


@owner_bp.route('/reports/export', methods=['POST'])
def export_report():
    result = OwnerDashboardController.export_report()
    payload = _extract_payload(result)
    message = payload.get('message')
    if result[1] >= 400:
        flash(message or 'Xuất báo cáo thất bại', 'error')
    else:
        flash(message or 'Đã xuất báo cáo', 'success')
    return _redirect_with_params('owner.statistics_report')

