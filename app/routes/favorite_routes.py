from flask import Blueprint, render_template, redirect, url_for, flash, request

from app.controllers.favorite_controller import FavoriteController

favorite_bp = Blueprint('favorite', __name__, url_prefix='/api/favorites')


def _extract_payload(result):
    try:
        return result[0].get_json()
    except Exception:
        return {}


def _render_with_messages(result):
    payload = _extract_payload(result)
    error = payload.get('message') if result[1] >= 400 else None
    success = payload.get('message') if result[1] < 400 else None
    return render_template('favorite/list.html', result=result, error=error, success=success)


def _flash_from_result(result, success_fallback, error_fallback):
    payload = _extract_payload(result)
    message = payload.get('message')
    if result[1] >= 400:
        flash(message or error_fallback, 'error')
    else:
        flash(message or success_fallback, 'success')


def _redirect_to_list():
    params = request.args.to_dict(flat=True)
    return redirect(url_for('favorite.favorite_list', **params))


@favorite_bp.route('/', methods=['GET'])
def favorite_list():
    result = FavoriteController.list_favorites()
    return _render_with_messages(result)


@favorite_bp.route('/', methods=['POST'])
def create_favorite():
    result = FavoriteController.add_favorite()
    _flash_from_result(result, 'Đã thêm yêu thích', 'Thêm yêu thích thất bại')
    return _redirect_to_list()


@favorite_bp.route('/<int:hotel_id>', methods=['POST', 'DELETE'])
def remove_favorite(hotel_id):
    result = FavoriteController.delete_favorite(hotel_id)
    _flash_from_result(result, 'Đã xóa yêu thích', 'Xóa yêu thích thất bại')
    return _redirect_to_list()


@favorite_bp.route('/toggle', methods=['POST'])
def toggle_favorite():
    result = FavoriteController.toggle_favorite()
    _flash_from_result(result, 'Đã cập nhật yêu thích', 'Không thể cập nhật yêu thích')
    return _redirect_to_list()

