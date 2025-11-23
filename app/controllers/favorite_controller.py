from flask import request, session
from marshmallow import ValidationError

from app import db
from app.models.favorite import Favorite
from app.models.hotel import Hotel
from app.schemas.favorite_schema import FavoriteCreateSchema
from app.utils.response import success_response, error_response, validation_error_response


class FavoriteController:
    @staticmethod
    def _get_request_data():
        data = {}
        if request.args:
            data.update(request.args.to_dict(flat=True))
        if request.form:
            form_data = dict(request.form)
            for key, value in form_data.items():
                if isinstance(value, list) and len(value) == 1:
                    form_data[key] = value[0]
            data.update(form_data)
        elif request.is_json:
            payload = request.get_json() or {}
            if isinstance(payload, dict):
                data.update(payload)
        return data

    @staticmethod
    def _require_login():
        if 'user_id' not in session:
            return error_response('Chưa đăng nhập', 401)
        return None

    @staticmethod
    def list_favorites():
        auth_error = FavoriteController._require_login()
        if auth_error:
            return auth_error
        try:
            data = FavoriteController._get_request_data()
            query = Favorite.query.filter_by(user_id=session['user_id'])

            hotel_id = data.get('hotel_id')
            if hotel_id:
                try:
                    hotel_id = int(hotel_id)
                    query = query.filter_by(hotel_id=hotel_id)
                except ValueError:
                    return error_response('hotel_id không hợp lệ', 400)

            favorites = query.order_by(Favorite.created_at.desc()).all()
            favorites_data = []
            for favorite in favorites:
                favorite_dict = favorite.to_dict()
                hotel = Hotel.query.get(favorite.hotel_id)
                favorite_dict['hotel'] = hotel.to_dict() if hotel else None
                favorites_data.append(favorite_dict)

            return success_response(
                data={'favorites': favorites_data},
                message='Lấy danh sách yêu thích thành công'
            )
        except Exception as exc:
            return error_response(f'Lỗi khi lấy danh sách yêu thích: {str(exc)}', 500)

    @staticmethod
    def add_favorite():
        auth_error = FavoriteController._require_login()
        if auth_error:
            return auth_error
        try:
            data = FavoriteController._get_request_data()
            schema = FavoriteCreateSchema()
            payload = schema.load(data)

            hotel = Hotel.query.get(payload['hotel_id'])
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)

            existing = Favorite.query.filter_by(
                user_id=session['user_id'],
                hotel_id=payload['hotel_id']
            ).first()
            if existing:
                return success_response(
                    data={'favorite': existing.to_dict()},
                    message='Khách sạn đã nằm trong danh sách yêu thích',
                    status_code=200
                )

            favorite = Favorite(
                user_id=session['user_id'],
                hotel_id=payload['hotel_id']
            )
            db.session.add(favorite)
            db.session.commit()

            favorite_dict = favorite.to_dict()
            favorite_dict['hotel'] = hotel.to_dict()

            return success_response(
                data={'favorite': favorite_dict},
                message='Đã thêm khách sạn vào danh sách yêu thích',
                status_code=201
            )
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Không thể thêm yêu thích: {str(exc)}', 500)

    @staticmethod
    def delete_favorite(hotel_id):
        auth_error = FavoriteController._require_login()
        if auth_error:
            return auth_error
        try:
            favorite = Favorite.query.filter_by(
                user_id=session['user_id'],
                hotel_id=hotel_id
            ).first()
            if not favorite:
                return error_response('Không tìm thấy yêu thích để xóa', 404)

            db.session.delete(favorite)
            db.session.commit()

            return success_response(message='Đã xóa yêu thích')
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Không thể xóa yêu thích: {str(exc)}', 500)

    @staticmethod
    def toggle_favorite():
        auth_error = FavoriteController._require_login()
        if auth_error:
            return auth_error
        try:
            data = FavoriteController._get_request_data()
            schema = FavoriteCreateSchema()
            payload = schema.load(data)

            favorite = Favorite.query.filter_by(
                user_id=session['user_id'],
                hotel_id=payload['hotel_id']
            ).first()

            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return success_response(message='Đã xóa khỏi danh sách yêu thích')

            hotel = Hotel.query.get(payload['hotel_id'])
            if not hotel:
                return error_response('Không tìm thấy khách sạn', 404)

            favorite = Favorite(
                user_id=session['user_id'],
                hotel_id=payload['hotel_id']
            )
            db.session.add(favorite)
            db.session.commit()

            favorite_dict = favorite.to_dict()
            favorite_dict['hotel'] = hotel.to_dict()

            return success_response(
                data={'favorite': favorite_dict},
                message='Đã thêm vào danh sách yêu thích',
                status_code=201
            )
        except ValidationError as exc:
            return validation_error_response(exc.messages)
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Không thể chuyển trạng thái yêu thích: {str(exc)}', 500)

