from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.user_controller import UserController
from app.utils.decorators import login_required

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        result = UserController.update_profile()
        try:
            result_data = result[0].get_json()
            if result[1] == 200:
                user = result_data.get('data', {}).get('user', {})
                return render_template('user/profile.html', user=user, result=result, success='Cập nhật profile thành công')
            else:
                error_message = result_data.get('message', 'Cập nhật profile thất bại')
                result_get = UserController.get_profile()
                user_data = result_get[0].get_json() if result_get and result_get[0] else {}
                user = user_data.get('data', {}).get('user', {})
                return render_template('user/profile.html', user=user, result=result, error=error_message)
        except:
            result_get = UserController.get_profile()
            user_data = result_get[0].get_json() if result_get and result_get[0] else {}
            user = user_data.get('data', {}).get('user', {})
            return render_template('user/profile.html', user=user, result=result, error='Cập nhật profile thất bại')
    
    result = UserController.get_profile()
    user_data = result[0].get_json() if result and result[0] else {}
    user = user_data.get('data', {}).get('user', {})
    return render_template('user/profile.html', user=user, result=result)

@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        result = UserController.change_password()
        try:
            result_data = result[0].get_json()
            if result[1] == 200:
                flash('Đổi mật khẩu thành công', 'success')
                return redirect(url_for('user.profile'))
            else:
                error_message = result_data.get('message', 'Đổi mật khẩu thất bại')
                return render_template('user/change_password.html', error=error_message)
        except:
            return render_template('user/change_password.html', error='Đổi mật khẩu thất bại')
    return render_template('user/change_password.html')

@user_bp.route('/upload-avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    if request.method == 'POST':
        result = UserController.upload_avatar()
        try:
            result_data = result[0].get_json()
            if result[1] == 200:
                flash('Tải lên avatar thành công', 'success')
                return redirect(url_for('user.profile'))
            else:
                error_message = result_data.get('message', 'Tải lên avatar thất bại')
                result_get = UserController.get_profile()
                user_data = result_get[0].get_json() if result_get and result_get[0] else {}
                user = user_data.get('data', {}).get('user', {})
                return render_template('user/upload_avatar.html', user=user, error=error_message)
        except:
            result_get = UserController.get_profile()
            user_data = result_get[0].get_json() if result_get and result_get[0] else {}
            user = user_data.get('data', {}).get('user', {})
            return render_template('user/upload_avatar.html', user=user, error='Tải lên avatar thất bại')
    
    result = UserController.get_profile()
    user_data = result[0].get_json() if result and result[0] else {}
    user = user_data.get('data', {}).get('user', {})
    return render_template('user/upload_avatar.html', user=user)

@user_bp.route('/bookings', methods=['GET'])
@login_required
def bookings():
    result = UserController.get_bookings()
    result_data = result[0].get_json() if result and result[0] else {}
    bookings_data = result_data.get('data', [])
    return render_template('user/bookings.html', bookings=bookings_data, result=result)

@user_bp.route('/favorites', methods=['GET'])
@login_required
def favorites():
    result = UserController.get_favorites()
    result_data = result[0].get_json() if result and result[0] else {}
    favorites_data = result_data.get('data', [])
    return render_template('user/favorites.html', favorites=favorites_data, result=result)

@user_bp.route('/notifications', methods=['GET'])
@login_required
def notifications():
    result = UserController.get_notifications()
    result_data = result[0].get_json() if result and result[0] else {}
    notifications_data = result_data.get('data', [])
    return render_template('user/notifications.html', notifications=notifications_data, result=result)

@user_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    result = UserController.mark_notification_read(notification_id)
    if result[1] == 200:
        flash('Đã đánh dấu đã đọc', 'success')
    else:
        flash('Thất bại', 'error')
    return redirect(url_for('user.notifications'))

@user_bp.route('/notifications/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    result = UserController.delete_notification(notification_id)
    if result[1] == 200:
        flash('Xóa thông báo thành công', 'success')
    else:
        flash('Xóa thông báo thất bại', 'error')
    return redirect(url_for('user.notifications'))

@user_bp.route('/search-history', methods=['GET'])
@login_required
def search_history():
    """Xem lịch sử tìm kiếm của user"""
    from app.controllers.search_controller import SearchController
    result = SearchController.get_search_history()
    result_data = result[0].get_json() if result and result[0] else {}
    history_data = result_data.get('data', [])
    return render_template('user/search_history.html', history=history_data, result=result)

@user_bp.route('/search-history/<int:search_id>/delete', methods=['POST'])
@login_required
def delete_search_history(search_id):
    """Xóa một lịch sử tìm kiếm"""
    from app.controllers.search_controller import SearchController
    result = SearchController.delete_search_history(search_id)
    if result[1] == 200:
        flash('Xóa lịch sử tìm kiếm thành công', 'success')
    else:
        flash('Xóa lịch sử tìm kiếm thất bại', 'error')
    return redirect(url_for('user.search_history'))