from flask import Blueprint, render_template, request
from app.utils.decorators import login_required

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/', methods=['GET'])
@login_required
def list_payments():
    return render_template('payment/list.html')

@payment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_payment():
    if request.method == 'POST':
        pass
    return render_template('payment/create.html')

@payment_bp.route('/<int:payment_id>', methods=['GET'])
@login_required
def payment_detail(payment_id):
    return render_template('payment/detail.html', payment_id=payment_id)

