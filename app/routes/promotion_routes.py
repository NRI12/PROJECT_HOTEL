from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.promotion_controller import PromotionController
from app.utils.decorators import login_required, role_required

promotion_bp = Blueprint('promotion', __name__, url_prefix='/promotion')

@promotion_bp.route('/', methods=['GET'])
def list_promotions():
    result = PromotionController.list_promotions()
    return render_template('promotion/list.html', result=result)

@promotion_bp.route('/<int:promotion_id>', methods=['GET'])
def promotion_detail(promotion_id):
    result = PromotionController.get_promotion(promotion_id)
    return render_template('promotion/detail.html', promotion_id=promotion_id, result=result)

@promotion_bp.route('/create', methods=['GET', 'POST'])
@role_required('admin', 'hotel_owner')
def create_promotion():
    if request.method == 'POST':
        result = PromotionController.create_promotion()
        if result[1] == 201:
            flash('Tạo khuyến mãi thành công', 'success')
            return redirect(url_for('promotion.list_promotions'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo khuyến mãi thất bại')
            except:
                error_message = 'Tạo khuyến mãi thất bại'
            return render_template('promotion/create.html', error=error_message)
    return render_template('promotion/create.html')

@promotion_bp.route('/<int:promotion_id>/edit', methods=['GET', 'POST'])
@role_required('admin', 'hotel_owner')
def edit_promotion(promotion_id):
    if request.method == 'POST':
        result = PromotionController.update_promotion(promotion_id)
        if result[1] == 200:
            flash('Cập nhật khuyến mãi thành công', 'success')
            return redirect(url_for('promotion.promotion_detail', promotion_id=promotion_id))
        else:
            flash('Cập nhật khuyến mãi thất bại', 'error')
    
    result = PromotionController.get_promotion(promotion_id)
    return render_template('promotion/edit.html', promotion_id=promotion_id, result=result)

@promotion_bp.route('/<int:promotion_id>/delete', methods=['POST'])
@role_required('admin', 'hotel_owner')
def delete_promotion(promotion_id):
    result = PromotionController.delete_promotion(promotion_id)
    if result[1] == 200:
        flash('Xóa khuyến mãi thành công', 'success')
    else:
        flash('Xóa khuyến mãi thất bại', 'error')
    return redirect(url_for('promotion.list_promotions'))

@promotion_bp.route('/active', methods=['GET'])
def active_promotions():
    result = PromotionController.get_active_promotions()
    return render_template('promotion/active.html', result=result)