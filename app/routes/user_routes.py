from flask import Blueprint
from app.controllers.user_controller import UserController

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

user_bp.route('/profile', methods=['GET'])(UserController.get_profile)
user_bp.route('/profile', methods=['PUT'])(UserController.update_profile)
user_bp.route('/change-password', methods=['PUT'])(UserController.change_password)
user_bp.route('/upload-avatar', methods=['POST'])(UserController.upload_avatar)
user_bp.route('/bookings', methods=['GET'])(UserController.get_bookings)
user_bp.route('/favorites', methods=['GET'])(UserController.get_favorites)
user_bp.route('/notifications', methods=['GET'])(UserController.get_notifications)
user_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])(UserController.mark_notification_read)
user_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])(UserController.delete_notification)


