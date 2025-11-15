from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET'])
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/users', methods=['GET'])
def users():
    return render_template('admin/users.html')

@admin_bp.route('/hotels', methods=['GET'])
def hotels():
    return render_template('admin/hotels.html')

@admin_bp.route('/bookings', methods=['GET'])
def bookings():
    return render_template('admin/bookings.html')

