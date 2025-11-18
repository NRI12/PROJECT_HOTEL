from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.discount_controller import DiscountController

discount_bp = Blueprint('discount', __name__, url_prefix='/discount')

@discount_bp.route('/', methods=['GET'])
def list_discounts():
    result = DiscountController.list_discounts()
    return render_template('discount/list.html', result=result)

@discount_bp.route('/<code>', methods=['GET'])
def discount_detail(code):
    result = DiscountController.get_discount_by_code(code)
    return render_template('discount/detail.html', code=code, result=result)

@discount_bp.route('/create', methods=['GET', 'POST'])
def create_discount():
    if request.method == 'POST':
        result = DiscountController.create_discount()
        if result[1] == 201:
            flash('Tạo mã giảm giá thành công', 'success')
            return redirect(url_for('discount.list_discounts'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo mã thất bại')
            except:
                error_message = 'Tạo mã thất bại'
            return render_template('discount/create.html', error=error_message)
    return render_template('discount/create.html')

@discount_bp.route('/edit/<int:code_id>', methods=['GET', 'POST'])
def edit_discount(code_id):
    if request.method == 'POST':
        result = DiscountController.update_discount(code_id)
        if result[1] == 200:
            flash('Cập nhật mã giảm giá thành công', 'success')
            return redirect(url_for('discount.list_discounts'))
        else:
            flash('Cập nhật mã thất bại', 'error')
            return redirect(url_for('discount.list_discounts'))
    return render_template('discount/edit.html', code_id=code_id)

@discount_bp.route('/delete/<int:code_id>', methods=['POST'])
def delete_discount(code_id):
    result = DiscountController.delete_discount(code_id)
    if result[1] == 200:
        flash('Xóa mã giảm giá thành công', 'success')
    else:
        flash('Xóa mã thất bại', 'error')
    return redirect(url_for('discount.list_discounts'))

@discount_bp.route('/validate', methods=['POST'])
def validate_discount():
    return DiscountController.validate_discount()

@discount_bp.route('/my-codes', methods=['GET'])
def my_codes():
    result = DiscountController.get_my_codes()
    return render_template('discount/my_codes.html', result=result)