from flask import Blueprint, render_template

notification_bp = Blueprint('notification', __name__, url_prefix='/notification')

@notification_bp.route('/', methods=['GET'])
def list_notifications():
    return render_template('notification/list.html')

@notification_bp.route('/<int:notification_id>', methods=['GET'])
def notification_detail(notification_id):
    return render_template('notification/detail.html', notification_id=notification_id)

