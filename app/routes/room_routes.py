from flask import Blueprint, render_template

room_bp = Blueprint('room', __name__, url_prefix='/room')

@room_bp.route('/', methods=['GET'])
def list_rooms():
    return render_template('room/list.html')

@room_bp.route('/<int:room_id>', methods=['GET'])
def room_detail(room_id):
    return render_template('room/detail.html', room_id=room_id)

