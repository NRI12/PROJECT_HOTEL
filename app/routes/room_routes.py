from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.room_controller import RoomController
from app.utils.decorators import hotel_owner_required

room_bp = Blueprint('room', __name__, url_prefix='/room')

@room_bp.route('/', methods=['GET'])
def list_rooms():
    result = RoomController.list_rooms()
    return render_template('room/list.html', result=result)

@room_bp.route('/<int:room_id>', methods=['GET'])
def room_detail(room_id):
    result = RoomController.get_room(room_id)
    return render_template('room/detail.html', room_id=room_id, result=result)

@room_bp.route('/create', methods=['GET', 'POST'])
def create_room():
    if request.method == 'POST':
        result = RoomController.create_room()
        if result[1] == 201:
            flash('Tạo phòng thành công', 'success')
            return redirect(url_for('room.list_rooms'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo phòng thất bại')
            except:
                error_message = 'Tạo phòng thất bại'
            return render_template('room/create.html', error=error_message)
    return render_template('room/create.html')

@room_bp.route('/<int:room_id>/edit', methods=['GET', 'POST'])
def edit_room(room_id):
    if request.method == 'POST':
        result = RoomController.update_room(room_id)
        if result[1] == 200:
            flash('Cập nhật phòng thành công', 'success')
            return redirect(url_for('room.room_detail', room_id=room_id))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Cập nhật phòng thất bại')
            except:
                error_message = 'Cập nhật phòng thất bại'
            return render_template('room/edit.html', room_id=room_id, error=error_message)
    
    result = RoomController.get_room(room_id)
    return render_template('room/edit.html', room_id=room_id, result=result)

@room_bp.route('/<int:room_id>/delete', methods=['POST'])
def delete_room(room_id):
    result = RoomController.delete_room(room_id)
    if result[1] == 200:
        flash('Xóa phòng thành công', 'success')
    else:
        flash('Xóa phòng thất bại', 'error')
    return redirect(url_for('room.list_rooms'))

@room_bp.route('/<int:room_id>/images', methods=['POST'])
def upload_images(room_id):
    result = RoomController.upload_images(room_id)
    if result[1] == 200:
        flash('Tải ảnh thành công', 'success')
    else:
        flash('Tải ảnh thất bại', 'error')
    return redirect(url_for('room.room_detail', room_id=room_id))

@room_bp.route('/<int:room_id>/images/<int:image_id>/delete', methods=['POST'])
def delete_image(room_id, image_id):
    result = RoomController.delete_image(room_id, image_id)
    if result[1] == 200:
        flash('Xóa ảnh thành công', 'success')
    else:
        flash('Xóa ảnh thất bại', 'error')
    return redirect(url_for('room.room_detail', room_id=room_id))

@room_bp.route('/<int:room_id>/amenities', methods=['GET'])
def room_amenities(room_id):
    result = RoomController.get_room_amenities(room_id)
    return render_template('room/amenities.html', room_id=room_id, result=result)

@room_bp.route('/<int:room_id>/amenities/update', methods=['POST'])
def update_amenities(room_id):
    result = RoomController.update_room_amenities(room_id)
    if result[1] == 200:
        flash('Cập nhật tiện nghi thành công', 'success')
    else:
        flash('Cập nhật tiện nghi thất bại', 'error')
    return redirect(url_for('room.room_amenities', room_id=room_id))

@room_bp.route('/<int:room_id>/availability', methods=['GET'])
def check_availability(room_id):
    result = RoomController.check_availability(room_id)
    return render_template('room/availability.html', room_id=room_id, result=result)

@room_bp.route('/<int:room_id>/status', methods=['POST'])
def update_status(room_id):
    result = RoomController.update_room_status(room_id)
    if result[1] == 200:
        flash('Cập nhật trạng thái thành công', 'success')
    else:
        flash('Cập nhật trạng thái thất bại', 'error')
    return redirect(url_for('room.room_detail', room_id=room_id))

@room_bp.route('/types', methods=['GET'])
def list_room_types():
    result = RoomController.list_room_types()
    return render_template('room/types_list.html', result=result)

@room_bp.route('/types/create', methods=['GET', 'POST'])
def create_room_type():
    if request.method == 'POST':
        result = RoomController.create_room_type()
        if result[1] == 201:
            flash('Tạo loại phòng thành công', 'success')
            return redirect(url_for('room.list_room_types'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo loại phòng thất bại')
            except:
                error_message = 'Tạo loại phòng thất bại'
            return render_template('room/types_create.html', error=error_message)
    return render_template('room/types_create.html')

@room_bp.route('/types/<int:type_id>/edit', methods=['GET', 'POST'])
def edit_room_type(type_id):
    if request.method == 'POST':
        result = RoomController.update_room_type(type_id)
        if result[1] == 200:
            flash('Cập nhật loại phòng thành công', 'success')
            return redirect(url_for('room.list_room_types'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Cập nhật loại phòng thất bại')
            except:
                error_message = 'Cập nhật loại phòng thất bại'
            result = RoomController.get_room_type(type_id)
            return render_template('room/types_edit.html', type_id=type_id, result=result, error=error_message)
    
    result = RoomController.get_room_type(type_id)
    return render_template('room/types_edit.html', type_id=type_id, result=result)

@room_bp.route('/types/<int:type_id>/delete', methods=['POST'])
def delete_room_type(type_id):
    result = RoomController.delete_room_type(type_id)
    if result[1] == 200:
        flash('Xóa loại phòng thành công', 'success')
    else:
        flash('Xóa loại phòng thất bại', 'error')
    return redirect(url_for('room.list_room_types'))

@room_bp.route('/amenities', methods=['GET'])
def list_amenities():
    result = RoomController.list_amenities()
    return render_template('room/amenities_list.html', result=result)

@room_bp.route('/amenities/create', methods=['GET', 'POST'])
def create_amenity():
    if request.method == 'POST':
        result = RoomController.create_amenity()
        if result[1] == 201:
            flash('Tạo tiện nghi thành công', 'success')
            return redirect(url_for('room.list_amenities'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo tiện nghi thất bại')
            except:
                error_message = 'Tạo tiện nghi thất bại'
            return render_template('room/amenities_create.html', error=error_message)
    return render_template('room/amenities_create.html')

@room_bp.route('/amenities/<int:amenity_id>/edit', methods=['GET', 'POST'])
def edit_amenity(amenity_id):
    if request.method == 'POST':
        result = RoomController.update_amenity(amenity_id)
        if result[1] == 200:
            flash('Cập nhật tiện nghi thành công', 'success')
            return redirect(url_for('room.list_amenities'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Cập nhật tiện nghi thất bại')
            except:
                error_message = 'Cập nhật tiện nghi thất bại'
            result = RoomController.get_amenity(amenity_id)
            return render_template('room/amenities_edit.html', amenity_id=amenity_id, result=result, error=error_message)
    
    result = RoomController.get_amenity(amenity_id)
    return render_template('room/amenities_edit.html', amenity_id=amenity_id, result=result)

@room_bp.route('/amenities/<int:amenity_id>/delete', methods=['POST'])
def delete_amenity(amenity_id):
    result = RoomController.delete_amenity(amenity_id)
    if result[1] == 200:
        flash('Xóa tiện nghi thành công', 'success')
    else:
        flash('Xóa tiện nghi thất bại', 'error')
    return redirect(url_for('room.list_amenities'))