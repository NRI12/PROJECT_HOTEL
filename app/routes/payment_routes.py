from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import login_required
from app.services.paypal_service import PayPalService
from app.models.booking import Booking
from app.models.payment import Payment
from app import db
from datetime import datetime

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/', methods=['GET'])
@login_required
def list_payments():
    return render_template('payment/list.html')

@payment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_payment():
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        booking_id = request.form.get('booking_id', type=int)
        
        if not booking_id:
            flash('Vui lòng nhập mã đặt phòng', 'error')
            return render_template('payment/create.html')
        
        booking = Booking.query.get(booking_id)
        if not booking:
            flash('Không tìm thấy đơn đặt phòng', 'error')
            return render_template('payment/create.html')
        
        if booking.user_id != session.get('user_id'):
            flash('Bạn không có quyền thanh toán đơn đặt phòng này', 'error')
            return render_template('payment/create.html')
        
        if payment_method == 'paypal':
            amount_usd = float(booking.final_amount) / 25000
            
            result = PayPalService.create_payment(amount_usd, booking.booking_code, booking_id=booking_id)
            
            if result['success']:
                session['paypal_booking_id'] = booking_id
                session.permanent = True
                session.modified = True
                return redirect(result['approval_url'])
            else:
                flash(f'Lỗi tạo thanh toán PayPal: {result.get("error", "Unknown error")}', 'error')
                return render_template('payment/create.html')
        
        flash('Phương thức thanh toán này chưa được hỗ trợ', 'error')
        return render_template('payment/create.html')
    
    return render_template('payment/create.html')

@payment_bp.route('/paypal-return', methods=['GET'])
def paypal_return():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')
    booking_id = request.args.get('booking_id', type=int) or session.get('paypal_booking_id')
    
    if not payment_id or not payer_id:
        flash('Thông tin thanh toán không hợp lệ', 'error')
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return redirect(url_for('payment.create_payment'))
    
    if not booking_id:
        existing_payment = Payment.query.filter_by(transaction_id=payment_id).first()
        if existing_payment:
            booking_id = existing_payment.booking_id
        else:
            flash('Không tìm thấy thông tin đặt phòng. Vui lòng đăng nhập lại.', 'error')
            return redirect(url_for('auth.login'))
    
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Không tìm thấy đơn đặt phòng', 'error')
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return redirect(url_for('payment.create_payment'))
    
    if 'user_id' in session and booking.user_id != session.get('user_id'):
        flash('Bạn không có quyền truy cập đơn đặt phòng này', 'error')
        return redirect(url_for('auth.login'))
    
    result = PayPalService.execute_payment(payment_id, payer_id)
    
    if result['success']:
        try:
            payment = Payment(
                booking_id=booking_id,
                payment_method='paypal',
                amount=booking.final_amount,
                transaction_id=payment_id,
                payment_status='completed',
                payment_date=datetime.utcnow(),
                notes=f'PayPal Payment ID: {payment_id}'
            )
            db.session.add(payment)
            booking.payment_status = 'paid'
            db.session.commit()
            session.pop('paypal_booking_id', None)
            
            booking_detail_url = url_for('booking.booking_detail', booking_id=booking_id)
            if 'user_id' in session:
                flash('Thanh toán thành công!', 'success')
                return redirect(booking_detail_url)
            else:
                from urllib.parse import quote
                flash('Thanh toán thành công! Vui lòng đăng nhập để xem chi tiết đặt phòng.', 'success')
                return redirect(url_for('auth.login', next=quote(booking_detail_url)))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi lưu thanh toán: {str(e)}', 'error')
            return redirect(url_for('payment.create_payment'))
    else:
        error_msg = result.get('error', 'Unknown error')
        flash(f'Thanh toán thất bại: {error_msg}', 'error')
        return redirect(url_for('payment.create_payment'))

@payment_bp.route('/paypal-cancel', methods=['GET'])
def paypal_cancel():
    booking_id = request.args.get('booking_id', type=int) or session.pop('paypal_booking_id', None)
    flash('Bạn đã hủy thanh toán', 'warning')
    
    if 'user_id' in session and booking_id:
        return redirect(url_for('booking.booking_detail', booking_id=booking_id))
    elif 'user_id' in session:
        return redirect(url_for('payment.create_payment'))
    elif booking_id:
        return redirect(url_for('booking.booking_detail', booking_id=booking_id))
    else:
        return redirect(url_for('auth.login'))

@payment_bp.route('/create-paypal', methods=['POST'])
@login_required
def create_paypal_payment():
    booking_id = request.form.get('booking_id', type=int)
    
    if not booking_id:
        flash('Vui lòng nhập mã đặt phòng', 'error')
        return redirect(url_for('payment.create_payment'))
    
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Không tìm thấy đơn đặt phòng', 'error')
        return redirect(url_for('payment.create_payment'))
    
    if booking.user_id != session.get('user_id'):
        flash('Bạn không có quyền thanh toán đơn đặt phòng này', 'error')
        return redirect(url_for('payment.create_payment'))
    
    amount_usd = float(booking.final_amount) / 25000
    
    result = PayPalService.create_payment(amount_usd, booking.booking_code, booking_id=booking_id)
    
    if result['success']:
        session['paypal_booking_id'] = booking_id
        session.permanent = True
        session.modified = True
        return redirect(result['approval_url'])
    else:
        flash(f'Lỗi tạo thanh toán PayPal: {result.get("error", "Unknown error")}', 'error')
        return redirect(url_for('payment.create_payment'))

@payment_bp.route('/success', methods=['GET'])
def payment_success():
    booking_id = request.args.get('booking_id', type=int)
    
    if not booking_id:
        flash('Không tìm thấy thông tin đặt phòng', 'error')
        return redirect(url_for('main.index'))
    
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Không tìm thấy đơn đặt phòng', 'error')
        return redirect(url_for('main.index'))
    
    booking_detail_url = url_for('booking.booking_detail', booking_id=booking_id)
    
    if 'user_id' in session:
        if booking.user_id == session.get('user_id'):
            flash('Thanh toán thành công!', 'success')
            return redirect(booking_detail_url)
        else:
            flash('Bạn không có quyền xem đơn đặt phòng này', 'error')
            return redirect(url_for('main.index'))
    
    from urllib.parse import quote
    login_with_next = url_for('auth.login', next=quote(booking_detail_url))
    
    return render_template('payment/success.html', 
                         booking_id=booking_id,
                         booking_code=booking.booking_code,
                         booking_detail_url=login_with_next)

@payment_bp.route('/<int:payment_id>', methods=['GET'])
@login_required
def payment_detail(payment_id):
    return render_template('payment/detail.html', payment_id=payment_id)

