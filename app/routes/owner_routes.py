from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.controllers.owner_controller import OwnerDashboardController
from app.utils.decorators import role_required

owner_bp = Blueprint('owner', __name__, url_prefix='/owner')


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
@role_required('hotel_owner', 'admin')
def dashboard():
    result = OwnerDashboardController.dashboard_overview()
    return _render_template(result, 'owner/dashboard.html')


@owner_bp.route('/hotels', methods=['GET'])
@role_required('hotel_owner', 'admin')
def my_hotels():
    result = OwnerDashboardController.my_hotels()
    return _render_template(result, 'owner/hotels.html')


@owner_bp.route('/bookings', methods=['GET'])
@role_required('hotel_owner', 'admin')
def owner_bookings():
    result = OwnerDashboardController.hotel_bookings()
    return _render_template(result, 'owner/bookings.html')


@owner_bp.route('/revenue', methods=['GET'])
@role_required('hotel_owner', 'admin')
def revenue_summary():
    result = OwnerDashboardController.revenue_summary()
    return _render_template(result, 'owner/revenue.html')


@owner_bp.route('/revenue/detail', methods=['GET'])
@role_required('hotel_owner', 'admin')
def revenue_detail():
    result = OwnerDashboardController.revenue_detail()
    return _render_template(result, 'owner/revenue_detail.html')


@owner_bp.route('/reviews', methods=['GET'])
@role_required('hotel_owner', 'admin')
def owner_reviews():
    result = OwnerDashboardController.hotel_reviews()
    return _render_template(result, 'owner/reviews.html')


@owner_bp.route('/statistics', methods=['GET'])
@role_required('hotel_owner', 'admin')
def statistics_report():
    result = OwnerDashboardController.statistics_report()
    return _render_template(result, 'owner/statistics.html')


@owner_bp.route('/occupancy', methods=['GET'])
@role_required('hotel_owner', 'admin')
def occupancy_report():
    result = OwnerDashboardController.occupancy_report()
    return _render_template(result, 'owner/occupancy.html')


@owner_bp.route('/reports/export', methods=['POST'])
@role_required('hotel_owner', 'admin')
def export_report():
    result = OwnerDashboardController.export_report()
    payload = _extract_payload(result)
    message = payload.get('message')
    if result[1] >= 400:
        flash(message or 'Xuất báo cáo thất bại', 'error')
    else:
        flash(message or 'Đã xuất báo cáo', 'success')
    return _redirect_with_params('owner.statistics_report')


# ==================== ROOMS ====================
@owner_bp.route('/rooms', methods=['GET'])
@role_required('hotel_owner', 'admin')
def owner_rooms():
    from app.controllers.room_controller import RoomController
    result = RoomController.list_rooms()
    return _render_template(result, 'owner/rooms.html')

@owner_bp.route('/rooms/create', methods=['GET', 'POST'])
@role_required('hotel_owner', 'admin')
def owner_rooms_create():
    from app.controllers.room_controller import RoomController
    from app.controllers.owner_controller import OwnerDashboardController
    from app.models.room_type import RoomType
    from app.models.amenity import Amenity
    
    # Get data for form
    hotels_result = OwnerDashboardController.my_hotels()
    hotels = []
    if hotels_result[1] == 200:
        payload = hotels_result[0].get_json()
        hotels = payload.get('data', {}).get('hotels', [])
    
    room_types = RoomType.query.all()
    room_types_data = [rt.to_dict() for rt in room_types]
    
    # Get amenities for room category
    amenities = Amenity.query.filter(
        (Amenity.category == 'room') | (Amenity.category == 'both')
    ).all()
    amenities_data = [a.to_dict() for a in amenities]
    
    if request.method == 'POST':
        print("=== DEBUG: Room Create Data ===")
        print(f"Form data: {dict(request.form)}")
        print(f"Files: {request.files}")
        print("=" * 50)
        
        result = RoomController.create_room()
        if result[1] == 201:
            flash('Tạo phòng thành công', 'success')
            return redirect(url_for('owner.owner_rooms'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo phòng thất bại')
            except:
                error_message = 'Tạo phòng thất bại'
            return render_template('owner/rooms_create.html', 
                                 error=error_message, 
                                 hotels=hotels, 
                                 room_types=room_types_data,
                                 amenities=amenities_data)
    
    return render_template('owner/rooms_create.html', 
                         hotels=hotels, 
                         room_types=room_types_data,
                         amenities=amenities_data)

@owner_bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@role_required('hotel_owner', 'admin')
def owner_rooms_edit(room_id):
    from app.controllers.room_controller import RoomController
    from app.controllers.owner_controller import OwnerDashboardController
    from app.models.room_type import RoomType
    
    if request.method == 'POST':
        result = RoomController.update_room(room_id)
        if result[1] == 200:
            flash('Cập nhật phòng thành công', 'success')
            return redirect(url_for('owner.owner_rooms'))
        flash('Cập nhật phòng thất bại', 'error')
    
    result = RoomController.get_room(room_id)
    
    # Get data for form
    hotels_result = OwnerDashboardController.my_hotels()
    hotels = []
    if hotels_result[1] == 200:
        payload = hotels_result[0].get_json()
        hotels = payload.get('data', {}).get('hotels', [])
    
    room_types = RoomType.query.all()
    room_types_data = [rt.to_dict() for rt in room_types]
    
    return _render_template(result, 'owner/rooms_edit.html', 
                          room_id=room_id, hotels=hotels, room_types=room_types_data)


@owner_bp.route('/rooms/<int:room_id>/delete', methods=['POST'])
@role_required('hotel_owner', 'admin')
def owner_rooms_delete(room_id):
    from app.controllers.room_controller import RoomController
    result = RoomController.delete_room(room_id)
    flash('Xóa phòng thành công' if result[1] == 200 else 'Xóa phòng thất bại', 
          'success' if result[1] == 200 else 'error')
    return redirect(url_for('owner.owner_rooms'))

@owner_bp.route('/rooms/<int:room_id>/status', methods=['POST'])
@role_required('hotel_owner', 'admin')
def owner_rooms_update_status(room_id):
    from app.controllers.room_controller import RoomController
    result = RoomController.update_room_status(room_id)
    return result


# ==================== AMENITIES ====================
@owner_bp.route('/amenities', methods=['GET'])
@role_required('hotel_owner', 'admin')
def owner_amenities():
    from app.controllers.room_controller import RoomController
    result = RoomController.list_amenities()
    return _render_template(result, 'owner/amenities.html')


@owner_bp.route('/amenities/create', methods=['GET', 'POST'])
@role_required('hotel_owner', 'admin')
def owner_amenities_create():
    from app.controllers.room_controller import RoomController
    if request.method == 'POST':
        result = RoomController.create_amenity()
        if result[1] == 201:
            flash('Tạo tiện nghi thành công', 'success')
            return redirect(url_for('owner.owner_amenities'))
        flash('Tạo tiện nghi thất bại', 'error')
    return render_template('owner/amenities_create.html')


@owner_bp.route('/amenities/<int:amenity_id>/edit', methods=['GET', 'POST'])
@role_required('hotel_owner', 'admin')
def owner_amenities_edit(amenity_id):
    from app.controllers.room_controller import RoomController
    if request.method == 'POST':
        result = RoomController.update_amenity(amenity_id)
        if result[1] == 200:
            flash('Cập nhật tiện nghi thành công', 'success')
            return redirect(url_for('owner.owner_amenities'))
        flash('Cập nhật tiện nghi thất bại', 'error')
    result = RoomController.get_amenity(amenity_id)
    return _render_template(result, 'owner/amenities_edit.html', amenity_id=amenity_id)


@owner_bp.route('/amenities/<int:amenity_id>/delete', methods=['POST'])
@role_required('hotel_owner', 'admin')
def owner_amenities_delete(amenity_id):
    from app.controllers.room_controller import RoomController
    result = RoomController.delete_amenity(amenity_id)
    flash('Xóa tiện nghi thành công' if result[1] == 200 else 'Xóa tiện nghi thất bại',
          'success' if result[1] == 200 else 'error')
    return redirect(url_for('owner.owner_amenities'))


# ==================== PROMOTIONS ====================
@owner_bp.route('/promotions', methods=['GET'])
@role_required('hotel_owner', 'admin')
def owner_promotions():
    from app.controllers.promotion_controller import PromotionController
    result = PromotionController.list_promotions()
    return _render_template(result, 'owner/promotions.html')


@owner_bp.route('/promotions/create', methods=['GET', 'POST'])
@role_required('hotel_owner', 'admin')
def owner_promotions_create():
    from app.controllers.promotion_controller import PromotionController
    if request.method == 'POST':
        result = PromotionController.create_promotion()
        if result[1] == 201:
            flash('Tạo khuyến mãi thành công', 'success')
            return redirect(url_for('owner.owner_promotions'))
        flash('Tạo khuyến mãi thất bại', 'error')
    return render_template('owner/promotions_create.html')


@owner_bp.route('/promotions/<int:promotion_id>/edit', methods=['GET', 'POST'])
@role_required('hotel_owner', 'admin')
def owner_promotions_edit(promotion_id):
    from app.controllers.promotion_controller import PromotionController
    if request.method == 'POST':
        result = PromotionController.update_promotion(promotion_id)
        if result[1] == 200:
            flash('Cập nhật khuyến mãi thành công', 'success')
            return redirect(url_for('owner.owner_promotions'))
        flash('Cập nhật khuyến mãi thất bại', 'error')
    result = PromotionController.get_promotion(promotion_id)
    return _render_template(result, 'owner/promotions_edit.html', promotion_id=promotion_id)


@owner_bp.route('/promotions/<int:promotion_id>/delete', methods=['POST'])
@role_required('hotel_owner', 'admin')
def owner_promotions_delete(promotion_id):
    from app.controllers.promotion_controller import PromotionController
    result = PromotionController.delete_promotion(promotion_id)
    flash('Xóa khuyến mãi thành công' if result[1] == 200 else 'Xóa khuyến mãi thất bại',
          'success' if result[1] == 200 else 'error')
    return redirect(url_for('owner.owner_promotions'))


# ==================== DISCOUNTS ====================
@owner_bp.route('/discounts', methods=['GET'])
@role_required('hotel_owner', 'admin')
def owner_discounts():
    from app.controllers.discount_controller import DiscountController
    result = DiscountController.list_discounts()
    return _render_template(result, 'owner/discounts.html')


@owner_bp.route('/discounts/create', methods=['GET', 'POST'])
@role_required('hotel_owner', 'admin')
def owner_discounts_create():
    from app.controllers.discount_controller import DiscountController
    if request.method == 'POST':
        result = DiscountController.create_discount()
        if result[1] == 201:
            flash('Tạo mã giảm giá thành công', 'success')
            return redirect(url_for('owner.owner_discounts'))
        flash('Tạo mã giảm giá thất bại', 'error')
    return render_template('owner/discounts_create.html')


@owner_bp.route('/discounts/<int:code_id>/edit', methods=['GET', 'POST'])
@role_required('hotel_owner', 'admin')
def owner_discounts_edit(code_id):
    from app.controllers.discount_controller import DiscountController
    if request.method == 'POST':
        result = DiscountController.update_discount(code_id)
        if result[1] == 200:
            flash('Cập nhật mã giảm giá thành công', 'success')
            return redirect(url_for('owner.owner_discounts'))
        flash('Cập nhật mã giảm giá thất bại', 'error')
    result = DiscountController.get_discount(code_id)
    return _render_template(result, 'owner/discounts_edit.html', code_id=code_id)


@owner_bp.route('/discounts/<int:code_id>/delete', methods=['POST'])
@role_required('hotel_owner', 'admin')
def owner_discounts_delete(code_id):
    from app.controllers.discount_controller import DiscountController
    result = DiscountController.delete_discount(code_id)
    flash('Xóa mã giảm giá thành công' if result[1] == 200 else 'Xóa mã giảm giá thất bại',
          'success' if result[1] == 200 else 'error')
    return redirect(url_for('owner.owner_discounts'))


# ==================== REVIEWS ====================
@owner_bp.route('/reviews/<int:review_id>/reply', methods=['POST'])
@role_required('hotel_owner', 'admin')
def owner_reviews_reply(review_id):
    from app.controllers.review_controller import ReviewController
    result = ReviewController.reply_review(review_id)
    flash('Phản hồi thành công' if result[1] == 200 else 'Phản hồi thất bại',
          'success' if result[1] == 200 else 'error')
    return redirect(url_for('owner.owner_reviews'))