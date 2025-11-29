from flask import request, session
from app import db
from app.models.booking import Booking
from app.models.booking_detail import BookingDetail
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.user import User
from app.models.payment import Payment
from app.models.discount_code import DiscountCode
from app.models.discount_usage import DiscountUsage
from app.schemas.booking_schema import (
    BookingCreateSchema, BookingUpdateSchema, CheckPriceSchema, 
    BookingValidateSchema, BookingCancelSchema
)
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from datetime import datetime, date
from sqlalchemy import and_, or_
import random
import string
import re

class BookingController:
    
    @staticmethod
    def _get_request_data():
        if request.form:
            data = dict(request.form)
            
            # Parse nested arrays like rooms[0][room_id]
            parsed_data = {}
            rooms_data = []
            guests_data = []
            
            for key, value in data.items():
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                
                # Parse rooms array
                if key.startswith('rooms[') and ']' in key:
                    match = re.match(r'rooms\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index = int(match.group(1))
                        field = match.group(2)
                        while len(rooms_data) <= index:
                            rooms_data.append({})
                        if field in ['room_id', 'quantity']:
                            rooms_data[index][field] = int(value) if value else 0
                        else:
                            rooms_data[index][field] = value
                        continue
                
                # Parse guests array
                if key.startswith('guests[') and ']' in key:
                    match = re.match(r'guests\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index = int(match.group(1))
                        field = match.group(2)
                        while len(guests_data) <= index:
                            guests_data.append({})
                        guests_data[index][field] = value
                        continue
                
                # Regular fields
                parsed_data[key] = value
            
            # Add parsed arrays
            if rooms_data:
                # Filter out empty dicts but keep dicts with room_id
                parsed_data['rooms'] = [r for r in rooms_data if r and r.get('room_id')]
            if guests_data:
                parsed_data['guests'] = [g for g in guests_data if g]
            
            return parsed_data
        elif request.is_json:
            return request.get_json() or {}
        else:
            return {}
    
    @staticmethod
    def _generate_booking_code():
        return 'BK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    @staticmethod
    def list_bookings():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            status = request.args.get('status')
            
            user = User.query.get(session['user_id'])
            
            if user.role.role_name == 'admin':
                query = Booking.query
            else:
                query = Booking.query.filter_by(user_id=session['user_id'])
            
            if status:
                query = query.filter_by(status=status)
            
            query = query.order_by(Booking.created_at.desc())
            
            total = query.count()
            bookings = query.offset((page - 1) * per_page).limit(per_page).all()
            
            bookings_data = []
            for booking in bookings:
                booking_dict = booking.to_dict()
                booking_dict['hotel'] = booking.hotel.to_dict() if booking.hotel else None
                booking_dict['user'] = booking.user.to_dict() if booking.user else None
                booking_dict['details'] = [detail.to_dict() for detail in booking.booking_details]
                bookings_data.append(booking_dict)
            
            return paginated_response(bookings_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách booking: {str(e)}', 500)
    
    @staticmethod
    def get_booking(booking_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            user = User.query.get(session['user_id'])
            
            if user.role.role_name != 'admin' and booking.user_id != session['user_id']:
                hotel = Hotel.query.get(booking.hotel_id)
                if not hotel or hotel.owner_id != session['user_id']:
                    return error_response('Không có quyền xem booking này', 403)
            
            booking_dict = booking.to_dict()
            booking_dict['hotel'] = booking.hotel.to_dict() if booking.hotel else None
            booking_dict['user'] = booking.user.to_dict() if booking.user else None
            booking_dict['details'] = [detail.to_dict() for detail in booking.booking_details]
            booking_dict['payments'] = [payment.to_dict() for payment in booking.payments]
            
            # Include discount usage information
            discount_usages = []
            for usage in booking.discount_usage:
                usage_dict = usage.to_dict()
                if usage.discount_code:
                    usage_dict['discount_code'] = usage.discount_code.to_dict()
                discount_usages.append(usage_dict)
            booking_dict['discount_usage'] = discount_usages
            
            return success_response(data={'booking': booking_dict})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy chi tiết booking: {str(e)}', 500)
    
    @staticmethod
    def create_booking():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            data = BookingController._get_request_data()
            
            required_fields = ['hotel_id', 'check_in_date', 'check_out_date', 'num_guests', 'rooms']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = BookingCreateSchema()
            validated_data = schema.load(data)
            
            check_in = validated_data['check_in_date']
            check_out = validated_data['check_out_date']
            
            if check_in >= check_out:
                return error_response('Ngày check-out phải sau ngày check-in', 400)
            
            if check_in < date.today():
                return error_response('Ngày check-in không được trong quá khứ', 400)
            
            num_nights = (check_out - check_in).days
            total_amount = 0
            booking_details = []
            check_in_datetime = datetime.combine(check_in, datetime.min.time())
            check_out_datetime = datetime.combine(check_out, datetime.min.time())
            
            # Calculate base prices first
            for room_data in validated_data['rooms']:
                room = Room.query.get(room_data['room_id'])
                if not room:
                    return error_response(f'Không tìm thấy phòng ID {room_data["room_id"]}', 404)
                
                if room.hotel_id != validated_data['hotel_id']:
                    return error_response('Phòng không thuộc khách sạn này', 400)
                
                quantity = room_data['quantity']
                price_per_night = room.base_price
                subtotal = float(price_per_night) * quantity * num_nights
                total_amount += subtotal
                
                booking_details.append({
                    'room_id': room.room_id,
                    'quantity': quantity,
                    'price_per_night': price_per_night,
                    'num_nights': num_nights,
                    'subtotal': subtotal
                })
            
            # Apply promotions (check for each room)
            promotion_discount_total = 0
            from app.models.promotion import Promotion
            from sqlalchemy import or_, and_
            
            for room_data in validated_data['rooms']:
                room = Room.query.get(room_data['room_id'])
                quantity = room_data['quantity']
                room_subtotal = float(room.base_price) * quantity * num_nights
                
                # Find active promotions for this room
                promotion_query = Promotion.query.filter(
                    Promotion.is_active == True,
                    Promotion.start_date <= check_out_datetime,
                    Promotion.end_date >= check_in_datetime,
                    or_(
                        Promotion.room_id == room.room_id,
                        and_(Promotion.hotel_id == validated_data['hotel_id'], Promotion.room_id.is_(None))
                    )
                )
                
                best_discount = 0
                for promo in promotion_query.all():
                    # Check min_nights
                    if promo.min_nights and num_nights < promo.min_nights:
                        continue
                    
                    # Check applicable_days if specified
                    if promo.applicable_days:
                        check_in_weekday = check_in.weekday()
                        applicable_days_list = [int(d.strip()) for d in promo.applicable_days.split(',') if d.strip().isdigit()]
                        if applicable_days_list and check_in_weekday not in applicable_days_list:
                            continue
                    
                    # Calculate discount for this room
                    if promo.discount_type == 'percentage':
                        discount = room_subtotal * (float(promo.discount_value) / 100)
                    else:  # fixed
                        discount = float(promo.discount_value) * quantity  # Apply per room
                    
                    if discount > best_discount:
                        best_discount = discount
                
                promotion_discount_total += best_discount
            
            # Apply promotion discount
            total_amount_after_promotion = total_amount - promotion_discount_total
            
            # Xử lý discount code nếu có (áp dụng sau promotion)
            discount_amount = 0
            discount_code_obj = None
            
            if validated_data.get('discount_code'):
                discount_code_str = validated_data['discount_code']
                discount_code_obj = DiscountCode.query.filter_by(code=discount_code_str, is_active=True).first()
                
                if discount_code_obj:
                    # Check if discount belongs to hotel owner
                    hotel = Hotel.query.get(validated_data['hotel_id'])
                    if not hotel:
                        return error_response('Không tìm thấy khách sạn', 404)
                    
                    if hotel.owner_id != discount_code_obj.owner_id:
                        return error_response('Mã giảm giá không áp dụng cho khách sạn này', 400)
                    
                    # Kiểm tra validity
                    now = datetime.utcnow()
                    if discount_code_obj.start_date <= now <= discount_code_obj.end_date:
                        # Kiểm tra minimum order amount (sau khi áp dụng promotion)
                        if total_amount_after_promotion >= (discount_code_obj.min_order_amount or 0):
                            # Kiểm tra usage limit
                            if not discount_code_obj.usage_limit or discount_code_obj.used_count < discount_code_obj.usage_limit:
                                # Tính discount (dựa trên tổng sau promotion)
                                if discount_code_obj.discount_type == 'percentage':
                                    discount_amount = total_amount_after_promotion * (discount_code_obj.discount_value / 100)
                                else:  # fixed
                                    discount_amount = discount_code_obj.discount_value
                                
                                # Áp dụng max discount nếu có
                                if discount_code_obj.max_discount_amount:
                                    discount_amount = min(discount_amount, discount_code_obj.max_discount_amount)
            
            final_amount = total_amount_after_promotion - discount_amount
            total_discount = promotion_discount_total + discount_amount
            booking_code = BookingController._generate_booking_code()
            
            booking = Booking(
                booking_code=booking_code,
                user_id=session['user_id'],
                hotel_id=validated_data['hotel_id'],
                check_in_date=check_in,
                check_out_date=check_out,
                num_guests=validated_data['num_guests'],
                total_amount=total_amount,
                discount_amount=total_discount,
                final_amount=final_amount,
                special_requests=validated_data.get('special_requests'),
                status='confirmed'  # INSTANT CONFIRM - Changed from 'pending'
            )
            
            db.session.add(booking)
            db.session.flush()
            
            for detail_data in booking_details:
                detail = BookingDetail(
                    booking_id=booking.booking_id,
                    **detail_data
                )
                db.session.add(detail)
            
            # Lưu discount usage nếu có
            if discount_code_obj and discount_amount > 0:
                discount_usage = DiscountUsage(
                    code_id=discount_code_obj.code_id,
                    user_id=session['user_id'],
                    booking_id=booking.booking_id,
                    discount_amount=discount_amount
                )
                db.session.add(discount_usage)
                
                # Tăng used_count
                discount_code_obj.used_count += 1
            
            db.session.commit()
            
            return success_response(
                data={'booking': booking.to_dict()},
                message='Tạo booking thành công',
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo booking thất bại: {str(e)}', 500)
    
    @staticmethod
    def check_price(booking_id):
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            data = BookingController._get_request_data()
            schema = CheckPriceSchema()
            validated_data = schema.load(data)
            
            check_in = validated_data.get('check_in_date', booking.check_in_date)
            check_out = validated_data.get('check_out_date', booking.check_out_date)
            num_nights = (check_out - check_in).days
            
            total_amount = 0
            breakdown = []
            
            for detail in booking.booking_details:
                room = Room.query.get(detail.room_id)
                price = room.base_price
                subtotal = price * detail.quantity * num_nights
                total_amount += subtotal
                
                breakdown.append({
                    'room_id': room.room_id,
                    'room_name': room.room_name,
                    'quantity': detail.quantity,
                    'price_per_night': float(price),
                    'num_nights': num_nights,
                    'subtotal': float(subtotal)
                })
            
            return success_response(data={
                'total_amount': float(total_amount),
                'breakdown': breakdown,
                'num_nights': num_nights
            })
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            return error_response(f'Lỗi kiểm tra giá: {str(e)}', 500)
    
    @staticmethod
    def update_booking(booking_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            if booking.user_id != session['user_id']:
                return error_response('Không có quyền cập nhật booking này', 403)
            
            if booking.status not in ['pending', 'confirmed']:
                return error_response('Không thể cập nhật booking với trạng thái hiện tại', 400)
            
            data = BookingController._get_request_data()
            schema = BookingUpdateSchema()
            validated_data = schema.load(data)
            
            for key, value in validated_data.items():
                if hasattr(booking, key):
                    setattr(booking, key, value)
            
            db.session.commit()
            
            return success_response(
                data={'booking': booking.to_dict()},
                message='Cập nhật booking thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật booking thất bại: {str(e)}', 500)
    
    @staticmethod
    def cancel_booking(booking_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            if booking.user_id != session['user_id']:
                return error_response('Không có quyền hủy booking này', 403)
            
            if booking.status in ['cancelled', 'checked_in', 'checked_out']:
                return error_response('Không thể hủy booking với trạng thái hiện tại', 400)
            
            data = BookingController._get_request_data()
            schema = BookingCancelSchema()
            validated_data = schema.load(data)
            
            booking.status = 'cancelled'
            booking.cancellation_reason = validated_data.get('reason')
            booking.cancelled_at = datetime.utcnow()
            
            db.session.commit()
            
            return success_response(message='Hủy booking thành công')
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Hủy booking thất bại: {str(e)}', 500)
    
    # INSTANT CONFIRM - No longer need this function
    # @staticmethod
    # def confirm_booking(booking_id):
    #     if 'user_id' not in session:
    #         return error_response('Chưa đăng nhập', 401)
    #     
    #     try:
    #         booking = Booking.query.get(booking_id)
    #         if not booking:
    #             return error_response('Không tìm thấy booking', 404)
    #         
    #         hotel = Hotel.query.get(booking.hotel_id)
    #         if hotel.owner_id != session['user_id']:
    #             user = User.query.get(session['user_id'])
    #             if not user or user.role.role_name != 'admin':
    #                 return error_response('Không có quyền xác nhận booking này', 403)
    #         
    #         if booking.status != 'pending':
    #             return error_response('Chỉ có thể xác nhận booking đang ở trạng thái pending', 400)
    #         
    #         booking.status = 'confirmed'
    #         db.session.commit()
    #         
    #         return success_response(message='Xác nhận booking thành công')
    #         
    #     except Exception as e:
    #         db.session.rollback()
    #         return error_response(f'Xác nhận booking thất bại: {str(e)}', 500)
    
    @staticmethod
    def check_in(booking_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            hotel = Hotel.query.get(booking.hotel_id)
            if hotel.owner_id != session['user_id']:
                user = User.query.get(session['user_id'])
                if not user or user.role.role_name != 'admin':
                    return error_response('Không có quyền check-in booking này', 403)
            
            if booking.status != 'confirmed':
                return error_response('Chỉ có thể check-in booking đã xác nhận', 400)
            
            booking.status = 'checked_in'
            db.session.commit()
            
            return success_response(message='Check-in thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Check-in thất bại: {str(e)}', 500)
    
    @staticmethod
    def check_out(booking_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            hotel = Hotel.query.get(booking.hotel_id)
            if hotel.owner_id != session['user_id']:
                user = User.query.get(session['user_id'])
                if not user or user.role.role_name != 'admin':
                    return error_response('Không có quyền check-out booking này', 403)
            
            if booking.status != 'checked_in':
                return error_response('Chỉ có thể check-out booking đã check-in', 400)
            
            booking.status = 'checked_out'
            db.session.commit()
            
            return success_response(message='Check-out thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Check-out thất bại: {str(e)}', 500)
    
    @staticmethod
    def get_invoice(booking_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            user = User.query.get(session['user_id'])
            
            if user.role.role_name != 'admin' and booking.user_id != session['user_id']:
                hotel = Hotel.query.get(booking.hotel_id)
                if not hotel or hotel.owner_id != session['user_id']:
                    return error_response('Không có quyền xem hóa đơn', 403)
            
            invoice = {
                'booking_code': booking.booking_code,
                'hotel': booking.hotel.to_dict() if booking.hotel else None,
                'customer': booking.user.to_dict() if booking.user else None,
                'check_in_date': booking.check_in_date.isoformat(),
                'check_out_date': booking.check_out_date.isoformat(),
                'num_guests': booking.num_guests,
                'details': [],
                'total_amount': float(booking.total_amount),
                'discount_amount': float(booking.discount_amount),
                'final_amount': float(booking.final_amount),
                'payments': [p.to_dict() for p in booking.payments]
            }
            
            for detail in booking.booking_details:
                room = Room.query.get(detail.room_id)
                invoice['details'].append({
                    'room_name': room.room_name if room else 'N/A',
                    'quantity': detail.quantity,
                    'price_per_night': float(detail.price_per_night),
                    'num_nights': detail.num_nights,
                    'subtotal': float(detail.subtotal)
                })
            
            return success_response(data={'invoice': invoice})
            
        except Exception as e:
            return error_response(f'Lỗi xuất hóa đơn: {str(e)}', 500)
    
    @staticmethod
    def resend_confirmation(booking_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            if booking.user_id != session['user_id']:
                return error_response('Không có quyền gửi lại email', 403)
            
            return success_response(message='Đã gửi lại email xác nhận')
            
        except Exception as e:
            return error_response(f'Gửi email thất bại: {str(e)}', 500)
    
    @staticmethod
    def validate_booking():
        try:
            data = BookingController._get_request_data()
            
            schema = BookingValidateSchema()
            validated_data = schema.load(data)
            
            check_in = validated_data['check_in_date']
            check_out = validated_data['check_out_date']
            
            if check_in >= check_out:
                return error_response('Ngày check-out phải sau ngày check-in', 400)
            
            if check_in < date.today():
                return error_response('Ngày check-in không được trong quá khứ', 400)
            
            hotel = Hotel.query.get(validated_data['hotel_id'])
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)
            
            for room_data in validated_data['rooms']:
                room = Room.query.get(room_data['room_id'])
                if not room:
                    return error_response(f'Không tìm thấy phòng ID {room_data["room_id"]}', 404)
                
                if room.hotel_id != validated_data['hotel_id']:
                    return error_response('Phòng không thuộc khách sạn này', 400)
            
            return success_response(message='Dữ liệu booking hợp lệ')
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            return error_response(f'Lỗi validate: {str(e)}', 500)
    
    @staticmethod
    def validate_contact():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            data = BookingController._get_request_data()
            errors = {}
            
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            current_user_id = session['user_id']
            
            # Validate email exists in system (but allow current user's email)
            if email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.user_id != current_user_id:
                    errors['email'] = 'Email này đã được sử dụng bởi tài khoản khác'
            
            # Validate phone exists in system (but allow current user's phone)
            if phone:
                existing_user = User.query.filter_by(phone=phone).first()
                if existing_user and existing_user.user_id != current_user_id:
                    errors['phone'] = 'Số điện thoại này đã được sử dụng bởi tài khoản khác'
            
            if errors:
                return validation_error_response(errors)
            
            return success_response(message='Thông tin liên hệ hợp lệ')
            
        except Exception as e:
            return error_response(f'Lỗi validate: {str(e)}', 500)