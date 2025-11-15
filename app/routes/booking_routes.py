from flask import Blueprint, render_template, request

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

@booking_bp.route('/', methods=['GET'])
def list_bookings():
    return render_template('booking/list.html')

@booking_bp.route('/create', methods=['GET', 'POST'])
def create_booking():
    if request.method == 'POST':
        pass
    return render_template('booking/create.html')

@booking_bp.route('/<int:booking_id>', methods=['GET'])
def booking_detail(booking_id):
    return render_template('booking/detail.html', booking_id=booking_id)

