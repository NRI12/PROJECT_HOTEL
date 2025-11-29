from flask import request, session
from app import db
from app.models.review import Review
from app.models.booking import Booking
from app.models.hotel import Hotel
from app.models.user import User
from app.schemas.review_schema import (
    ReviewCreateSchema, ReviewUpdateSchema, ReviewResponseSchema, ReviewReportSchema
)
from app.utils.response import success_response, error_response, paginated_response, validation_error_response
from app.utils.validators import validate_required_fields
from marshmallow import ValidationError
from datetime import datetime

class ReviewController:
    
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
    def list_reviews():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            hotel_id = request.args.get('hotel_id', type=int)
            user_id = request.args.get('user_id', type=int)
            status = request.args.get('status')
            
            query = Review.query
            
            if hotel_id:
                query = query.filter_by(hotel_id=hotel_id)
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            else:
                query = query.filter_by(status='active')
            
            query = query.order_by(Review.created_at.desc())
            
            total = query.count()
            reviews = query.offset((page - 1) * per_page).limit(per_page).all()
            
            reviews_data = []
            for review in reviews:
                review_dict = review.to_dict()
                if review.user:
                    review_dict['user'] = {
                        'user_id': review.user.user_id,
                        'name': review.user.full_name or review.user.email,
                        'email': review.user.email,
                        'full_name': review.user.full_name
                    }
                else:
                    review_dict['user'] = None
                if review.hotel:
                    review_dict['hotel'] = {
                        'hotel_id': review.hotel.hotel_id,
                        'hotel_name': review.hotel.hotel_name,
                        'city': review.hotel.city
                    }
                else:
                    review_dict['hotel'] = None
                reviews_data.append(review_dict)
            
            return paginated_response(reviews_data, page, per_page, total)
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy danh sách review: {str(e)}', 500)
    
    @staticmethod
    def get_review(review_id):
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy review', 404)
            
            review_dict = review.to_dict()
            review_dict['user'] = review.user.to_dict() if review.user else None
            review_dict['hotel'] = review.hotel.to_dict() if review.hotel else None
            review_dict['booking'] = review.booking.to_dict() if review.booking else None
            
            return success_response(data={'review': review_dict})
            
        except Exception as e:
            return error_response(f'Lỗi khi lấy chi tiết review: {str(e)}', 500)
    
    @staticmethod
    def create_review():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            data = ReviewController._get_request_data()
            
            required_fields = ['booking_id', 'rating']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = ReviewCreateSchema()
            validated_data = schema.load(data)
            
            booking = Booking.query.get(validated_data['booking_id'])
            if not booking:
                return error_response('Không tìm thấy booking', 404)
            
            if booking.user_id != session['user_id']:
                return error_response('Không có quyền review booking này', 403)
            
            if booking.status != 'checked_out':
                return error_response('Chỉ có thể review booking đã check-out', 400)
            
            existing_review = Review.query.filter_by(booking_id=validated_data['booking_id']).first()
            if existing_review:
                return error_response('Booking này đã được review', 409)
            
            review = Review(
                booking_id=validated_data['booking_id'],
                user_id=session['user_id'],
                hotel_id=booking.hotel_id,
                rating=validated_data['rating'],
                cleanliness_rating=validated_data.get('cleanliness_rating'),
                service_rating=validated_data.get('service_rating'),
                facilities_rating=validated_data.get('facilities_rating'),
                location_rating=validated_data.get('location_rating'),
                comment=validated_data.get('comment'),
                status='active'
            )
            
            db.session.add(review)
            db.session.commit()
            
            return success_response(
                data={'review': review.to_dict()},
                message='Tạo review thành công',
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Tạo review thất bại: {str(e)}', 500)
    
    @staticmethod
    def update_review(review_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy review', 404)
            
            if review.user_id != session['user_id']:
                return error_response('Không có quyền cập nhật review này', 403)
            
            data = ReviewController._get_request_data()
            schema = ReviewUpdateSchema()
            validated_data = schema.load(data)
            
            for key, value in validated_data.items():
                if hasattr(review, key):
                    setattr(review, key, value)
            
            db.session.commit()
            
            return success_response(
                data={'review': review.to_dict()},
                message='Cập nhật review thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật review thất bại: {str(e)}', 500)
    
    @staticmethod
    def delete_review(review_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy review', 404)
            
            user = User.query.get(session['user_id'])
            
            if review.user_id != session['user_id'] and user.role.role_name != 'admin':
                return error_response('Không có quyền xóa review này', 403)
            
            db.session.delete(review)
            db.session.commit()
            
            return success_response(message='Xóa review thành công')
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Xóa review thất bại: {str(e)}', 500)
    
    @staticmethod
    def add_response(review_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy review', 404)
            
            hotel = Hotel.query.get(review.hotel_id)
            if hotel.owner_id != session['user_id']:
                user = User.query.get(session['user_id'])
                if not user or user.role.role_name != 'admin':
                    return error_response('Không có quyền phản hồi review này', 403)
            
            data = ReviewController._get_request_data()
            
            required_fields = ['response']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = ReviewResponseSchema()
            validated_data = schema.load(data)
            
            review.hotel_response = validated_data['response']
            review.response_date = datetime.utcnow()
            
            db.session.commit()
            
            return success_response(
                data={'review': review.to_dict()},
                message='Phản hồi review thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Phản hồi review thất bại: {str(e)}', 500)
    
    @staticmethod
    def update_response(review_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy review', 404)
            
            hotel = Hotel.query.get(review.hotel_id)
            if hotel.owner_id != session['user_id']:
                user = User.query.get(session['user_id'])
                if not user or user.role.role_name != 'admin':
                    return error_response('Không có quyền cập nhật phản hồi', 403)
            
            if not review.hotel_response:
                return error_response('Review chưa có phản hồi', 400)
            
            data = ReviewController._get_request_data()
            
            required_fields = ['response']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = ReviewResponseSchema()
            validated_data = schema.load(data)
            
            review.hotel_response = validated_data['response']
            review.response_date = datetime.utcnow()
            
            db.session.commit()
            
            return success_response(
                data={'review': review.to_dict()},
                message='Cập nhật phản hồi thành công'
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Cập nhật phản hồi thất bại: {str(e)}', 500)
    
    @staticmethod
    def report_review(review_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy review', 404)
            
            data = ReviewController._get_request_data()
            
            required_fields = ['reason']
            is_valid, error_msg = validate_required_fields(data, required_fields)
            if not is_valid:
                return error_response(error_msg, 400)
            
            schema = ReviewReportSchema()
            validated_data = schema.load(data)
            
            review.is_reported = True
            review.report_reason = validated_data['reason']
            
            db.session.commit()
            
            return success_response(message='Báo cáo review thành công')
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(f'Báo cáo review thất bại: {str(e)}', 500)
    
    @staticmethod
    def mark_helpful(review_id):
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        
        try:
            review = Review.query.get(review_id)
            if not review:
                return error_response('Không tìm thấy review', 404)
            
            return success_response(message='Đánh dấu review hữu ích thành công')
            
        except Exception as e:
            return error_response(f'Lỗi: {str(e)}', 500)
    
    @staticmethod
    def reply_review(review_id):
        """Alias for add_response - for owner routes compatibility"""
        return ReviewController.add_response(review_id)