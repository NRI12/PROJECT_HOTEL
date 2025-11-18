from flask import request, session
from app import db
from app.models.discount_code import DiscountCode
from app.models.discount_usage import DiscountUsage
from app.models.user import User
from app.schemas.discount_schema import DiscountCreateSchema, DiscountUpdateSchema, DiscountValidateSchema
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from datetime import datetime

class DiscountController:
    
    @staticmethod
    def _get_request_data():
        if request.form:
            data = dict(request.form)
            for key, value in data.items():
                if isinstance(value, list) and len(value) == 1:
                    data[key] = value[0]
            return data
        elif request.is_json:
            return request.get_json() or {}
        else:
            return {}
    
    @staticmethod
    def list_discounts():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            is_active = request.args.get('is_active', type=lambda v: v.lower() == 'true')
            
            query = DiscountCode.query
            
            if is_active is not None:
                query = query.filter_by(is_active=is_active)
            
            query = query.order_by(DiscountCode.created_at.desc())
            
            total = query.count()
            discounts = query.offset((page - 1) * per_page).limit(per_page).all()
            
            discounts_data = [d.to_dict() for d in discounts]
            
            return paginated_response(discounts_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách mã giảm giá: {str(e)}', 500)
    
    @staticmethod
    def get_discount_by_code(code):
        try:
            discount = DiscountCode.query.filter_by(code=code).first()
            if not discount:
                return error_response('Không tìm thấy mã giảm giá', 404)
            
            return success_response(data={'discount': discount.to_dict()})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy mã giảm giá: {str(e)}', 500)
    
    @staticmethod
    def create_discount():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name not in ['admin', 'hotel_owner']:
            return error_response('Không có quyền tạo mã giảm giá', 403)
        
        try:
            data = DiscountController._get_request_data()
            
            required_fields = ['code', 'discount_type', 'discount_value', 'start_date', 'end_date']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = DiscountCreateSchema()
            validated_data = schema.load(data)
            
            existing = DiscountCode.query.filter_by(code=validated_data['code']).first()
            if existing:
                return error_response('Mã giảm giá đã tồn tại', 409)
            
            discount = DiscountCode(
                code=validated_data['code'],
                description=validated_data.get('description'),
                discount_type=validated_data['discount_type'],
                discount_value=validated_data['discount_value'],
                min_order_amount=validated_data.get('min_order_amount', 0),
                max_discount_amount=validated_data.get('max_discount_amount'),
                usage_limit=validated_data.get('usage_limit'),
                start_date=validated_data['start_date'],
                end_date=validated_data['end_date'],
                is_active=True
            )
            
            db.session.add(discount)
            db.session.commit()
            
            return success_response(
                data={'discount': discount.to_dict()},
                message='Tạo mã giảm giá thành công',
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo mã giảm giá thất bại: {str(e)}', 500)
    
    @staticmethod
    def update_discount(code_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name not in ['admin', 'hotel_owner']:
            return error_response('Không có quyền cập nhật mã giảm giá', 403)
        
        try:
            discount = DiscountCode.query.get(code_id)
            if not discount:
                return error_response('Không tìm thấy mã giảm giá', 404)
            
            data = DiscountController._get_request_data()
            schema = DiscountUpdateSchema()
            validated_data = schema.load(data)
            
            if 'code' in validated_data:
                existing = DiscountCode.query.filter(
                    DiscountCode.code == validated_data['code'],
                    DiscountCode.code_id != code_id
                ).first()
                if existing:
                    return error_response('Mã giảm giá đã tồn tại', 409)
            
            for key, value in validated_data.items():
                if hasattr(discount, key):
                    setattr(discount, key, value)
            
            db.session.commit()
            
            return success_response(
                data={'discount': discount.to_dict()},
                message='Cập nhật mã giảm giá thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật mã giảm giá thất bại: {str(e)}', 500)
    
    @staticmethod
    def delete_discount(code_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        user = User.query.get(session['user_id'])
        if not user or user.role.role_name not in ['admin', 'hotel_owner']:
            return error_response('Không có quyền xóa mã giảm giá', 403)
        
        try:
            discount = DiscountCode.query.get(code_id)
            if not discount:
                return error_response('Không tìm thấy mã giảm giá', 404)
            
            if discount.used_count > 0:
                return error_response('Không thể xóa mã giảm giá đã được sử dụng', 400)
            
            db.session.delete(discount)
            db.session.commit()
            
            return success_response(message='Xóa mã giảm giá thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa mã giảm giá thất bại: {str(e)}', 500)
    
    @staticmethod
    def validate_discount():
        try:
            data = DiscountController._get_request_data()
            
            required_fields = ['code', 'order_amount']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = DiscountValidateSchema()
            validated_data = schema.load(data)
            
            discount = DiscountCode.query.filter_by(code=validated_data['code']).first()
            if not discount:
                return error_response('Mã giảm giá không tồn tại', 404)
            
            if not discount.is_active:
                return error_response('Mã giảm giá không còn hiệu lực', 400)
            
            now = datetime.utcnow()
            if now < discount.start_date:
                return error_response('Mã giảm giá chưa có hiệu lực', 400)
            
            if now > discount.end_date:
                return error_response('Mã giảm giá đã hết hạn', 400)
            
            if discount.usage_limit and discount.used_count >= discount.usage_limit:
                return error_response('Mã giảm giá đã hết lượt sử dụng', 400)
            
            order_amount = validated_data['order_amount']
            if order_amount < discount.min_order_amount:
                return error_response(f'Đơn hàng tối thiểu {discount.min_order_amount}', 400)
            
            if discount.discount_type == 'percentage':
                discount_amount = order_amount * (discount.discount_value / 100)
                if discount.max_discount_amount:
                    discount_amount = min(discount_amount, discount.max_discount_amount)
            else:
                discount_amount = discount.discount_value
            
            discount_amount = min(discount_amount, order_amount)
            
            return success_response(data={
                'discount': discount.to_dict(),
                'discount_amount': float(discount_amount),
                'final_amount': float(order_amount - discount_amount)
            })
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            return error_response(f'Lỗi validate mã giảm giá: {str(e)}', 500)
    
    @staticmethod
    def get_my_codes():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            usage = DiscountUsage.query.filter_by(user_id=session['user_id']).all()
            
            codes_data = []
            for u in usage:
                discount = DiscountCode.query.get(u.code_id)
                if discount:
                    code_dict = discount.to_dict()
                    code_dict['used_at'] = u.used_at.isoformat() if u.used_at else None
                    code_dict['discount_amount'] = float(u.discount_amount)
                    codes_data.append(code_dict)
            
            return success_response(data={'codes': codes_data})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy mã của tôi: {str(e)}', 500)