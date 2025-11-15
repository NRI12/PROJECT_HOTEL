from flask import Blueprint, render_template, request

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/', methods=['GET'])
def list_payments():
    return render_template('payment/list.html')

@payment_bp.route('/create', methods=['GET', 'POST'])
def create_payment():
    if request.method == 'POST':
        pass
    return render_template('payment/create.html')

@payment_bp.route('/<int:payment_id>', methods=['GET'])
def payment_detail(payment_id):
    return render_template('payment/detail.html', payment_id=payment_id)

