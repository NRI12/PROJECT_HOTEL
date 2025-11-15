from flask import Blueprint, render_template

hotel_bp = Blueprint('hotel', __name__, url_prefix='/hotel')

@hotel_bp.route('/', methods=['GET'])
def list_hotels():
    return render_template('hotel/list.html')

@hotel_bp.route('/<int:hotel_id>', methods=['GET'])
def hotel_detail(hotel_id):
    return render_template('hotel/detail.html', hotel_id=hotel_id)

