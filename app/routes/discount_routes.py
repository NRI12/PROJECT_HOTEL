from flask import Blueprint, render_template, request

discount_bp = Blueprint('discount', __name__, url_prefix='/discount')

@discount_bp.route('/', methods=['GET'])
def list_discounts():
    return render_template('discount/list.html')

@discount_bp.route('/apply', methods=['GET', 'POST'])
def apply_discount():
    if request.method == 'POST':
        pass
    return render_template('discount/apply.html')

