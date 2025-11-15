from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.user_controller import UserController

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Token is now automatically read from cookies by Flask-JWT-Extended
# No need for manual injection

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        result = UserController.update_profile()
        if result[1] == 200:
            flash('Cập nhật profile thành công', 'success')
        else:
            flash('Cập nhật profile thất bại', 'error')
    result = UserController.get_profile()
    return render_template('user/profile.html', result=result)

@user_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        result = UserController.change_password()
        if result[1] == 200:
            flash('Đổi mật khẩu thành công', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Đổi mật khẩu thất bại', 'error')
    return render_template('user/change_password.html')

@user_bp.route('/upload-avatar', methods=['GET', 'POST'])
def upload_avatar():
    if request.method == 'POST':
        result = UserController.upload_avatar()
        if result[1] == 200:
            flash('Tải lên avatar thành công', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Tải lên avatar thất bại', 'error')
    return render_template('user/upload_avatar.html')

@user_bp.route('/bookings', methods=['GET'])
def bookings():
    result = UserController.get_bookings()
    return render_template('user/bookings.html', result=result)

@user_bp.route('/favorites', methods=['GET'])
def favorites():
    result = UserController.get_favorites()
    return render_template('user/favorites.html', result=result)

@user_bp.route('/notifications', methods=['GET'])
def notifications():
    result = UserController.get_notifications()
    return render_template('user/notifications.html', result=result)

@user_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    result = UserController.mark_notification_read(notification_id)
    if result[1] == 200:
        flash('Đã đánh dấu đã đọc', 'success')
    else:
        flash('Thất bại', 'error')
    return redirect(url_for('user.notifications'))

@user_bp.route('/notifications/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    result = UserController.delete_notification(notification_id)
    if result[1] == 200:
        flash('Xóa thông báo thành công', 'success')
    else:
        flash('Xóa thông báo thất bại', 'error')
    return redirect(url_for('user.notifications'))
