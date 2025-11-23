from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.booking_controller import BookingController
from app.utils.decorators import login_required, booking_owner_or_hotel_owner_required, role_required

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

@booking_bp.route('/', methods=['GET'])
@login_required
def list_bookings():
    result = BookingController.list_bookings()
    return render_template('booking/list.html', result=result)

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@booking_owner_or_hotel_owner_required
def booking_detail(booking_id):
    result = BookingController.get_booking(booking_id)
    return render_template('booking/detail.html', booking_id=booking_id, result=result)

@booking_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_booking():
    if request.method == 'POST':
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            result = BookingController.create_booking()
            return result
        
        result = BookingController.create_booking()
        if result[1] == 201:
            flash('Tạo booking thành công', 'success')
            booking_id = result[0].get_json()['data']['booking']['booking_id']
            return redirect(url_for('booking.booking_detail', booking_id=booking_id))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo booking thất bại')
            except:
                error_message = 'Tạo booking thất bại'
            
            # GET hotel và room data lại để render
            hotel_id = request.args.get('hotel_id', type=int)
            room_id = request.args.get('room_id', type=int)
            
            hotel_data = None
            room_data = None
            
            if hotel_id:
                from app.models.hotel import Hotel
                hotel = Hotel.query.get(hotel_id)
                if hotel:
                    hotel_data = hotel.to_dict()
                    hotel_data['images'] = [img.to_dict() for img in hotel.images]
            
            if room_id:
                from app.models.room import Room
                room = Room.query.get(room_id)
                if room:
                    room_data = room.to_dict()
                    room_data['images'] = [img.to_dict() for img in room.images]
                    room_data['amenities'] = [a.to_dict() for a in room.amenities]
            
            return render_template('booking/create.html', 
                                 hotel=hotel_data, 
                                 room=room_data,
                                 error=error_message)
    
    # GET request - render form
    hotel_id = request.args.get('hotel_id', type=int)
    room_id = request.args.get('room_id', type=int)
    
    hotel_data = None
    room_data = None
    
    if hotel_id:
        from app.models.hotel import Hotel
        hotel = Hotel.query.get(hotel_id)
        if hotel:
            hotel_data = hotel.to_dict()
            hotel_data['images'] = [img.to_dict() for img in hotel.images]
    
    if room_id:
        from app.models.room import Room
        room = Room.query.get(room_id)
        if room:
            room_data = room.to_dict()
            room_data['images'] = [img.to_dict() for img in room.images]
            room_data['amenities'] = [a.to_dict() for a in room.amenities]
    
    return render_template('booking/create.html', 
                         hotel=hotel_data, 
                         room=room_data)

@booking_bp.route('/<int:booking_id>/check-price', methods=['POST'])
def check_price(booking_id):
    result = BookingController.check_price(booking_id)
    return result

@booking_bp.route('/<int:booking_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_booking(booking_id):
    if request.method == 'POST':
        result = BookingController.update_booking(booking_id)
        if result[1] == 200:
            flash('Cập nhật booking thành công', 'success')
            return redirect(url_for('booking.booking_detail', booking_id=booking_id))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Cập nhật booking thất bại')
            except:
                error_message = 'Cập nhật booking thất bại'
            result = BookingController.get_booking(booking_id)
            return render_template('booking/edit.html', booking_id=booking_id, result=result, error=error_message)
    
    result = BookingController.get_booking(booking_id)
    return render_template('booking/edit.html', booking_id=booking_id, result=result)

@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    result = BookingController.cancel_booking(booking_id)
    if result[1] == 200:
        flash('Hủy booking thành công', 'success')
    else:
        flash('Hủy booking thất bại', 'error')
    return redirect(url_for('booking.booking_detail', booking_id=booking_id))

# INSTANT CONFIRM - No longer need confirm route
# @booking_bp.route('/<int:booking_id>/confirm', methods=['POST'])
# @role_required('admin', 'hotel_owner')
# def confirm_booking(booking_id):
#     result = BookingController.confirm_booking(booking_id)
#     if result[1] == 200:
#         flash('Xác nhận booking thành công', 'success')
#     else:
#         flash('Xác nhận booking thất bại', 'error')
#     return redirect(url_for('booking.booking_detail', booking_id=booking_id))

@booking_bp.route('/<int:booking_id>/check-in', methods=['POST'])
@role_required('admin', 'hotel_owner')
def check_in(booking_id):
    result = BookingController.check_in(booking_id)
    if result[1] == 200:
        flash('Check-in thành công', 'success')
    else:
        flash('Check-in thất bại', 'error')
    return redirect(url_for('booking.booking_detail', booking_id=booking_id))

@booking_bp.route('/<int:booking_id>/check-out', methods=['POST'])
@role_required('admin', 'hotel_owner')
def check_out(booking_id):
    result = BookingController.check_out(booking_id)
    if result[1] == 200:
        flash('Check-out thành công', 'success')
    else:
        flash('Check-out thất bại', 'error')
    return redirect(url_for('booking.booking_detail', booking_id=booking_id))

@booking_bp.route('/<int:booking_id>/invoice', methods=['GET'])
@booking_owner_or_hotel_owner_required
def invoice(booking_id):
    result = BookingController.get_invoice(booking_id)
    return render_template('booking/invoice.html', booking_id=booking_id, result=result)

@booking_bp.route('/<int:booking_id>/resend-confirmation', methods=['POST'])
@login_required
def resend_confirmation(booking_id):
    result = BookingController.resend_confirmation(booking_id)
    if result[1] == 200:
        flash('Đã gửi lại email xác nhận', 'success')
    else:
        flash('Gửi email thất bại', 'error')
    return redirect(url_for('booking.booking_detail', booking_id=booking_id))

@booking_bp.route('/validate', methods=['POST'])
def validate_booking():
    return BookingController.validate_booking()