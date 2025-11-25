from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.controllers.hotel_controller import HotelController
from app.utils.decorators import role_required, hotel_owner_required

hotel_bp = Blueprint('hotel', __name__, url_prefix='/hotel')

@hotel_bp.route('/', methods=['GET'])
def list_hotels():
    result = HotelController.list_hotels()
    return render_template('hotel/list.html', result=result)

@hotel_bp.route('/featured', methods=['GET'])
def featured_hotels():
    result = HotelController.get_featured_hotels()
    return render_template('hotel/featured.html', result=result)

@hotel_bp.route('/<int:hotel_id>', methods=['GET'])
def hotel_detail(hotel_id):
    result = HotelController.get_hotel(hotel_id)
    return render_template('hotel/detail.html', hotel_id=hotel_id, result=result)

@hotel_bp.route('/create', methods=['GET', 'POST'])
@role_required('admin', 'hotel_owner')
def create_hotel():
    if request.method == 'POST':
        result = HotelController.create_hotel()
        if result[1] == 201:
            flash('Tạo khách sạn thành công. Đang chờ duyệt.', 'success')
            # Lấy hotel_id từ response để redirect đến trang chi tiết
            try:
                response_data = result[0].get_json()
                hotel_id = response_data.get('data', {}).get('hotel', {}).get('hotel_id')
                if hotel_id:
                    return redirect(url_for('hotel.hotel_detail', hotel_id=hotel_id))
            except:
                pass
            # Fallback: redirect về danh sách khách sạn của owner
            return redirect(url_for('owner.my_hotels'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo khách sạn thất bại')
            except:
                error_message = 'Tạo khách sạn thất bại'
            return render_template('hotel/create.html', error=error_message)
    return render_template('hotel/create.html')

@hotel_bp.route('/<int:hotel_id>/edit', methods=['GET', 'POST'])
@hotel_owner_required
def edit_hotel(hotel_id):
    if request.method == 'POST':
        result = HotelController.update_hotel(hotel_id)
        if result[1] == 200:
            flash('Cập nhật khách sạn thành công', 'success')
            return redirect(url_for('hotel.hotel_detail', hotel_id=hotel_id))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Cập nhật khách sạn thất bại')
            except:
                error_message = 'Cập nhật khách sạn thất bại'
            return render_template('hotel/edit.html', hotel_id=hotel_id, error=error_message)
    
    result = HotelController.get_hotel(hotel_id)
    return render_template('hotel/edit.html', hotel_id=hotel_id, result=result)

@hotel_bp.route('/<int:hotel_id>/delete', methods=['POST'])
@hotel_owner_required
def delete_hotel(hotel_id):
    result = HotelController.delete_hotel(hotel_id)
    if result[1] == 200:
        flash('Xóa khách sạn thành công', 'success')
    else:
        flash('Xóa khách sạn thất bại', 'error')
    return redirect(url_for('hotel.list_hotels'))

@hotel_bp.route('/<int:hotel_id>/images', methods=['POST'])
@hotel_owner_required
def upload_images(hotel_id):
    result = HotelController.upload_images(hotel_id)
    if result[1] == 200:
        flash('Tải ảnh thành công', 'success')
    else:
        flash('Tải ảnh thất bại', 'error')
    return redirect(url_for('hotel.hotel_detail', hotel_id=hotel_id))

@hotel_bp.route('/<int:hotel_id>/images/<int:image_id>/delete', methods=['POST'])
@hotel_owner_required
def delete_image(hotel_id, image_id):
    result = HotelController.delete_image(hotel_id, image_id)
    if result[1] == 200:
        flash('Xóa ảnh thành công', 'success')
    else:
        flash('Xóa ảnh thất bại', 'error')
    return redirect(url_for('hotel.hotel_detail', hotel_id=hotel_id))

@hotel_bp.route('/<int:hotel_id>/images/<int:image_id>/primary', methods=['POST'])
@hotel_owner_required
def set_primary_image(hotel_id, image_id):
    result = HotelController.set_primary_image(hotel_id, image_id)
    if result[1] == 200:
        flash('Đặt ảnh chính thành công', 'success')
    else:
        flash('Đặt ảnh chính thất bại', 'error')
    return redirect(url_for('hotel.hotel_detail', hotel_id=hotel_id))

@hotel_bp.route('/<int:hotel_id>/reviews', methods=['GET'])
def hotel_reviews(hotel_id):
    result = HotelController.get_hotel_reviews(hotel_id)
    return render_template('hotel/reviews.html', hotel_id=hotel_id, result=result)


# API Endpoint for AJAX
@hotel_bp.route('/api/<int:hotel_id>/rooms', methods=['GET'])
def api_get_hotel_rooms(hotel_id):
    """API endpoint to get rooms for a specific hotel (for AJAX calls)"""
    from app.models.room import Room
    try:
        rooms = Room.query.filter_by(hotel_id=hotel_id).all()
        rooms_data = []
        for room in rooms:
            room_dict = room.to_dict()
            if room.room_type:
                room_dict['room_type'] = room.room_type.to_dict()
            rooms_data.append(room_dict)
        
        return jsonify({
            'success': True,
            'data': rooms_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@hotel_bp.route('/<int:hotel_id>/rooms', methods=['GET'])
def hotel_rooms(hotel_id):
    result = HotelController.get_hotel_rooms(hotel_id)
    print(result)
    return result
@hotel_bp.route('/<int:hotel_id>/amenities', methods=['GET', 'POST'])
def hotel_amenities(hotel_id):
    from app.models.amenity import Amenity
    
    if request.method == 'POST':
        result = HotelController.update_hotel_amenities(hotel_id)
        if result[1] == 200:
            flash('Cập nhật tiện nghi thành công', 'success')
            return redirect(url_for('hotel.hotel_detail', hotel_id=hotel_id))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Cập nhật tiện nghi thất bại')
            except:
                error_message = 'Cập nhật tiện nghi thất bại'
            all_amenities = Amenity.query.all()
            result = HotelController.get_hotel_amenities(hotel_id)
            return render_template('hotel/amenities.html', hotel_id=hotel_id, result=result, all_amenities=all_amenities, error=error_message)
    
    result = HotelController.get_hotel_amenities(hotel_id)
    all_amenities = Amenity.query.all()
    return render_template('hotel/amenities.html', hotel_id=hotel_id, result=result, all_amenities=all_amenities)

@hotel_bp.route('/<int:hotel_id>/amenities/update', methods=['POST'])
@hotel_owner_required
def update_amenities(hotel_id):
    result = HotelController.update_hotel_amenities(hotel_id)
    if result[1] == 200:
        flash('Cập nhật tiện nghi thành công', 'success')
    else:
        flash('Cập nhật tiện nghi thất bại', 'error')
    return redirect(url_for('hotel.hotel_amenities', hotel_id=hotel_id))

@hotel_bp.route('/<int:hotel_id>/policies', methods=['GET'])
def hotel_policies(hotel_id):
    result = HotelController.get_hotel_policies(hotel_id)
    return render_template('hotel/policies.html', hotel_id=hotel_id, result=result)

@hotel_bp.route('/<int:hotel_id>/policies/create', methods=['POST'])
@hotel_owner_required
def create_policy(hotel_id):
    result = HotelController.create_hotel_policy(hotel_id)
    if result[1] == 201:
        flash('Tạo chính sách thành công', 'success')
    else:
        flash('Tạo chính sách thất bại', 'error')
    return redirect(url_for('hotel.hotel_policies', hotel_id=hotel_id))