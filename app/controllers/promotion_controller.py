from flask import request, session
from app import db
from app.models.promotion import Promotion
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.user import User
from app.schemas.promotion_schema import PromotionCreateSchema, PromotionUpdateSchema
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from datetime import datetime

class PromotionController:
    
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
    def _preprocess_form_data(data):
        """Convert empty strings to None for optional integer fields"""
        optional_int_fields = ['hotel_id', 'room_id', 'min_nights']
        for field in optional_int_fields:
            if field in data and data[field] == '':
                data[field] = None
        return data
    
    @staticmethod
    def list_promotions():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            hotel_id = request.args.get('hotel_id', type=int)
            room_id = request.args.get('room_id', type=int)
            is_active = request.args.get('is_active', type=lambda v: v.lower() == 'true')
            
            query = Promotion.query
            
            if hotel_id:
                query = query.filter_by(hotel_id=hotel_id)
            
            if room_id:
                query = query.filter_by(room_id=room_id)
            
            if is_active is not None:
                query = query.filter_by(is_active=is_active)
            
            query = query.order_by(Promotion.created_at.desc())
            
            total = query.count()
            promotions = query.offset((page - 1) * per_page).limit(per_page).all()
            
            promotions_data = []
            for promo in promotions:
                promo_dict = promo.to_dict()
                if promo.hotel:
                    promo_dict['hotel'] = promo.hotel.to_dict()
                if promo.room:
                    promo_dict['room'] = promo.room.to_dict()
                promotions_data.append(promo_dict)
            
            return paginated_response(promotions_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách khuyến mãi: {str(e)}', 500)
    
    @staticmethod
    def get_promotion(promotion_id):
        try:
            promotion = Promotion.query.get(promotion_id)
            if not promotion:
                return error_response('Không tìm thấy khuyến mãi', 404)
            
            promo_dict = promotion.to_dict()
            if promotion.hotel:
                promo_dict['hotel'] = promotion.hotel.to_dict()
            if promotion.room:
                promo_dict['room'] = promotion.room.to_dict()
            
            return success_response(data={'promotion': promo_dict})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy chi tiết khuyến mãi: {str(e)}', 500)
    
    @staticmethod
    def create_promotion():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            data = PromotionController._get_request_data()
            data = PromotionController._preprocess_form_data(data)
            
            required_fields = ['title', 'discount_type', 'discount_value', 'start_date', 'end_date']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = PromotionCreateSchema()
            validated_data = schema.load(data)
            
            if validated_data.get('hotel_id'):
                hotel = Hotel.query.get(validated_data['hotel_id'])
                if not hotel:
                    return error_response('Không tìm thấy khách sạn', 404)
                
                if hotel.owner_id != session['user_id']:
                    user = User.query.get(session['user_id'])
                    if not user or user.role.role_name != 'admin':
                        return error_response('Không có quyền tạo khuyến mãi cho khách sạn này', 403)
            
            if validated_data.get('room_id'):
                room = Room.query.get(validated_data['room_id'])
                if not room:
                    return error_response('Không tìm thấy phòng', 404)
                
                if room.hotel.owner_id != session['user_id']:
                    user = User.query.get(session['user_id'])
                    if not user or user.role.role_name != 'admin':
                        return error_response('Không có quyền tạo khuyến mãi cho phòng này', 403)
            
            promotion = Promotion(
                hotel_id=validated_data.get('hotel_id'),
                room_id=validated_data.get('room_id'),
                title=validated_data['title'],
                description=validated_data.get('description'),
                discount_type=validated_data['discount_type'],
                discount_value=validated_data['discount_value'],
                start_date=validated_data['start_date'],
                end_date=validated_data['end_date'],
                applicable_days=validated_data.get('applicable_days'),
                min_nights=validated_data.get('min_nights', 1),
                is_active=True
            )
            
            db.session.add(promotion)
            db.session.commit()
            
            return success_response(
                data={'promotion': promotion.to_dict()},
                message='Tạo khuyến mãi thành công',
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo khuyến mãi thất bại: {str(e)}', 500)
    
    @staticmethod
    def update_promotion(promotion_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            promotion = Promotion.query.get(promotion_id)
            if not promotion:
                return error_response('Không tìm thấy khuyến mãi', 404)
            
            if promotion.hotel_id:
                hotel = Hotel.query.get(promotion.hotel_id)
                if hotel.owner_id != session['user_id']:
                    user = User.query.get(session['user_id'])
                    if not user or user.role.role_name != 'admin':
                        return error_response('Không có quyền cập nhật khuyến mãi này', 403)
            
            if promotion.room_id:
                room = Room.query.get(promotion.room_id)
                if room.hotel.owner_id != session['user_id']:
                    user = User.query.get(session['user_id'])
                    if not user or user.role.role_name != 'admin':
                        return error_response('Không có quyền cập nhật khuyến mãi này', 403)
            
            data = PromotionController._get_request_data()
            data = PromotionController._preprocess_form_data(data)
            schema = PromotionUpdateSchema()
            validated_data = schema.load(data)
            
            for key, value in validated_data.items():
                if hasattr(promotion, key):
                    setattr(promotion, key, value)
            
            db.session.commit()
            
            return success_response(
                data={'promotion': promotion.to_dict()},
                message='Cập nhật khuyến mãi thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật khuyến mãi thất bại: {str(e)}', 500)
    
    @staticmethod
    def delete_promotion(promotion_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            promotion = Promotion.query.get(promotion_id)
            if not promotion:
                return error_response('Không tìm thấy khuyến mãi', 404)
            
            if promotion.hotel_id:
                hotel = Hotel.query.get(promotion.hotel_id)
                if hotel.owner_id != session['user_id']:
                    user = User.query.get(session['user_id'])
                    if not user or user.role.role_name != 'admin':
                        return error_response('Không có quyền xóa khuyến mãi này', 403)
            
            if promotion.room_id:
                room = Room.query.get(promotion.room_id)
                if room.hotel.owner_id != session['user_id']:
                    user = User.query.get(session['user_id'])
                    if not user or user.role.role_name != 'admin':
                        return error_response('Không có quyền xóa khuyến mãi này', 403)
            
            db.session.delete(promotion)
            db.session.commit()
            
            return success_response(message='Xóa khuyến mãi thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa khuyến mãi thất bại: {str(e)}', 500)
    
    @staticmethod
    def get_active_promotions():
        try:
            now = datetime.utcnow()
            
            promotions = Promotion.query.filter(
                Promotion.is_active == True,
                Promotion.start_date <= now,
                Promotion.end_date >= now
            ).all()
            
            promotions_data = []
            for promo in promotions:
                promo_dict = promo.to_dict()
                if promo.hotel:
                    promo_dict['hotel'] = promo.hotel.to_dict()
                if promo.room:
                    promo_dict['room'] = promo.room.to_dict()
                promotions_data.append(promo_dict)
            
            return success_response(data={'promotions': promotions_data})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy khuyến mãi đang hoạt động: {str(e)}', 500)