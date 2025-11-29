from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.booking_controller import BookingController
from app.utils.decorators import login_required, booking_owner_or_hotel_owner_required, role_required
from app.models.user import User

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
        # Handle step navigation (next/prev step)
        if 'next_step' in request.form:
            # Save current step data to session
            step = int(request.form.get('current_step', 1))
            if step == 1:
                # Parse room_id from nested form data - Flask treats it as a regular key
                room_id = request.form.get('rooms[0][room_id]') or request.args.get('room_id')
                
                session['booking_step1'] = {
                    'hotel_id': request.form.get('hotel_id'),
                    'num_guests': request.form.get('num_guests'),
                    'check_in_date': request.form.get('check_in_date'),
                    'check_out_date': request.form.get('check_out_date'),
                    'room_id': room_id,
                    'contact_name': request.form.get('contact_name'),
                    'contact_phone': request.form.get('contact_phone'),
                    'contact_email': request.form.get('contact_email'),
                    'special_requests': request.form.get('special_requests')
                }
                next_step = int(request.form.get('next_step'))
                return redirect(url_for('booking.create_booking', step=next_step, 
                                      hotel_id=request.form.get('hotel_id'),
                                      room_id=room_id))
            elif step == 2:
                session['booking_step2'] = {
                    'guest_name': request.form.get('guests[0][name]'),
                    'guest_id_number': request.form.get('guests[0][id_number]')
                }
                next_step = int(request.form.get('next_step'))
                return redirect(url_for('booking.create_booking', step=next_step,
                                      hotel_id=session.get('booking_step1', {}).get('hotel_id'),
                                      room_id=session.get('booking_step1', {}).get('room_id')))
        
        # Handle final submission
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            result = BookingController.create_booking()
            return result
        
        payment_method = request.form.get('payment_method', 'hotel')
        
        result = BookingController.create_booking()
        if result[1] == 201:
            booking_id = result[0].get_json()['data']['booking']['booking_id']
            booking = BookingController.get_booking(booking_id)
            booking_data = booking[0].get_json()['data']['booking']
            
            if payment_method == 'paypal':
                from app.services.paypal_service import PayPalService
                amount_usd = float(booking_data['final_amount']) / 25000
                
                result_paypal = PayPalService.create_payment(amount_usd, booking_data['booking_code'], booking_id=booking_id)
                
                if result_paypal['success']:
                    session['paypal_booking_id'] = booking_id
                    session.permanent = True
                    session.modified = True
                    session.pop('booking_step1', None)
                    session.pop('booking_step2', None)
                    return redirect(result_paypal['approval_url'])
                else:
                    flash(f'Lỗi tạo thanh toán PayPal: {result_paypal.get("error", "Unknown error")}', 'error')
                    session.pop('booking_step1', None)
                    session.pop('booking_step2', None)
                    return redirect(url_for('booking.booking_detail', booking_id=booking_id))
            
            if payment_method in ['vnpay', 'momo']:
                pass
            elif payment_method == 'hotel':
                pass
            
            flash('Tạo booking thành công', 'success')
            session.pop('booking_step1', None)
            session.pop('booking_step2', None)
            return redirect(url_for('booking.booking_detail', booking_id=booking_id))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo booking thất bại')
            except:
                error_message = 'Tạo booking thất bại'
            
            # Get step from session or default to 3
            step = request.args.get('step', 3, type=int)
            return redirect(url_for('booking.create_booking', step=step,
                                  hotel_id=session.get('booking_step1', {}).get('hotel_id'),
                                  room_id=session.get('booking_step1', {}).get('room_id'),
                                  error=error_message))
    
    # GET request - render form
    step = request.args.get('step', 1, type=int)
    hotel_id = request.args.get('hotel_id', type=int) or (int(session.get('booking_step1', {}).get('hotel_id')) if session.get('booking_step1', {}).get('hotel_id') else None)
    room_id = request.args.get('room_id', type=int) or (int(session.get('booking_step1', {}).get('room_id')) if session.get('booking_step1', {}).get('room_id') else None)
    
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
    
    # Get current user info
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    
    # Get today's date for min date
    from datetime import date
    today = date.today().isoformat()
    
    # Get saved form data from session
    step1_data = session.get('booking_step1', {})
    step2_data = session.get('booking_step2', {})
    
    # Calculate price for step 3
    price_info = None
    if step == 3 and room_data and step1_data.get('check_in_date') and step1_data.get('check_out_date'):
        from datetime import datetime
        from app.models.promotion import Promotion
        try:
            check_in = datetime.strptime(step1_data.get('check_in_date'), '%Y-%m-%d').date()
            check_out = datetime.strptime(step1_data.get('check_out_date'), '%Y-%m-%d').date()
            num_nights = (check_out - check_in).days
            
            if num_nights > 0 and room_data.get('base_price'):
                base_price = float(room_data.get('base_price', 0))
                total_amount = base_price * num_nights
                
                # Check for active promotions
                promotion_discount = 0
                active_promotion = None
                now = datetime.utcnow()
                check_in_datetime = datetime.combine(check_in, datetime.min.time())
                check_out_datetime = datetime.combine(check_out, datetime.min.time())
                
                # Query promotions for this room or hotel
                room_id_value = step1_data.get('room_id') or (room_data.get('room_id') if room_data else None)
                hotel_id_value = step1_data.get('hotel_id') or (hotel_data.get('hotel_id') if hotel_data else None)
                
                if room_id_value or hotel_id_value:
                    # Find active promotions
                    from sqlalchemy import or_, and_
                    
                    # Build filter conditions
                    date_filter = and_(
                        Promotion.is_active == True,
                        Promotion.start_date <= check_out_datetime,
                        Promotion.end_date >= check_in_datetime
                    )
                    
                    # Filter by room_id or hotel_id
                    if room_id_value and hotel_id_value:
                        # Check promotions for this specific room, or hotel-level promotions
                        promotion_filter = or_(
                            Promotion.room_id == room_id_value,
                            and_(Promotion.hotel_id == hotel_id_value, Promotion.room_id.is_(None))
                        )
                    elif room_id_value:
                        promotion_filter = Promotion.room_id == room_id_value
                    elif hotel_id_value:
                        promotion_filter = or_(
                            Promotion.hotel_id == hotel_id_value,
                            Promotion.hotel_id.is_(None)
                        )
                    else:
                        promotion_filter = True
                    
                    promotions = Promotion.query.filter(
                        date_filter,
                        promotion_filter
                    ).all()
                    
                    # Find the best promotion (highest discount)
                    best_discount = 0
                    for promo in promotions:
                        # Check min_nights
                        if promo.min_nights and num_nights < promo.min_nights:
                            continue
                        
                        # Check applicable_days if specified
                        if promo.applicable_days:
                            # applicable_days format: "0,1,2" (Monday=0, Sunday=6)
                            check_in_weekday = check_in.weekday()
                            applicable_days_list = [int(d.strip()) for d in promo.applicable_days.split(',') if d.strip().isdigit()]
                            if applicable_days_list and check_in_weekday not in applicable_days_list:
                                continue
                        
                        # Calculate discount
                        if promo.discount_type == 'percentage':
                            discount = total_amount * (float(promo.discount_value) / 100)
                        else:  # fixed
                            discount = float(promo.discount_value)
                        
                        if discount > best_discount:
                            best_discount = discount
                            active_promotion = promo
                    
                    promotion_discount = best_discount
                
                final_amount = total_amount - promotion_discount
                
                price_info = {
                    'base_price': base_price,
                    'num_nights': num_nights,
                    'total_amount': total_amount,
                    'promotion_discount': promotion_discount,
                    'discount_amount': promotion_discount,  # For compatibility
                    'final_amount': final_amount,
                    'promotion': active_promotion.to_dict() if active_promotion else None
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            pass
    
    return render_template('booking/create.html', 
                         hotel=hotel_data, 
                         room=room_data,
                         current_user=current_user.to_dict() if current_user else None,
                         today=today,
                         current_step=step,
                         step1_data=step1_data,
                         step2_data=step2_data,
                         price_info=price_info,
                         error=request.args.get('error'))

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

@booking_bp.route('/validate-contact', methods=['POST'])
@login_required
def validate_contact():
    return BookingController.validate_contact()