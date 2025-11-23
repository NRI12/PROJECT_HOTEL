from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.auth_controller import AuthController
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def _get_redirect_by_role(user):
    """Điều hướng user đến trang phù hợp theo role"""
    if not user or not user.role:
        return url_for('main.index')
    
    role_name = user.role.role_name
    
    # Admin -> Admin Dashboard
    if role_name == 'admin':
        return url_for('admin.admin_dashboard')
    
    # Hotel Owner -> Owner Dashboard
    elif role_name == 'hotel_owner':
        return url_for('owner.dashboard')
    
    # Customer -> User Dashboard (hoặc main index)
    elif role_name == 'customer':
        return url_for('user.dashboard')
    
    # Default -> Main Index
    else:
        return url_for('main.index')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        result = AuthController.register()
        if result[1] == 201:
            flash('Đăng ký thành công. Vui lòng kiểm tra email để xác thực tài khoản.', 'success')
            return redirect(url_for('auth.login'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Đăng ký thất bại')
            except:
                error_message = 'Đăng ký thất bại'
            return render_template('auth/register.html', error=error_message)
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = AuthController.login()
        if result[1] == 200:
            # Lấy thông tin user từ session để điều hướng đúng
            user_id = session.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                redirect_url = _get_redirect_by_role(user)
                flash('Đăng nhập thành công', 'success')
                return redirect(redirect_url)
            else:
                flash('Đăng nhập thành công', 'success')
                return redirect(url_for('main.index'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Đăng nhập thất bại')
            except:
                error_message = 'Đăng nhập thất bại'
            return render_template('auth/login.html', error=error_message)
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        AuthController.logout()
        return redirect(url_for('auth.login'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/refresh', methods=['GET', 'POST'])
def refresh():
    if request.method == 'POST':
        result = AuthController.refresh()
        return render_template('auth/refresh.html', result=result)
    return render_template('auth/refresh.html')

@auth_bp.route('/verify-token', methods=['GET'])
def verify_token():
    result = AuthController.verify_token()
    return render_template('auth/verify_token.html', result=result)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        result = AuthController.forgot_password()
        if result[1] == 200:
            return render_template('auth/forgot_password.html', success='Nếu email tồn tại, liên kết đặt lại mật khẩu đã được gửi.')
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Yêu cầu thất bại')
            except:
                error_message = 'Yêu cầu thất bại'
            return render_template('auth/forgot_password.html', error=error_message)
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        token = request.args.get('token', '')
        return render_template('auth/reset_password.html', token=token)
    
    if request.method == 'POST':
        result = AuthController.reset_password()
        if result[1] == 200:
            flash('Đặt lại mật khẩu thành công', 'success')
            return redirect(url_for('auth.login'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Đặt lại mật khẩu thất bại')
            except:
                error_message = 'Đặt lại mật khẩu thất bại'
            token = request.form.get('token', '')
            return render_template('auth/reset_password.html', error=error_message, token=token)

@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'GET':
        token = request.args.get('token', '')
        return render_template('auth/verify_email.html', token=token)
    
    if request.method == 'POST':
        result = AuthController.verify_email()
        if result[1] == 200:
            flash('Xác thực email thành công', 'success')
            return redirect(url_for('auth.login'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Xác thực email thất bại')
            except:
                error_message = 'Xác thực email thất bại'
            token = request.form.get('token', '')
            return render_template('auth/verify_email.html', error=error_message, token=token)

@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        result = AuthController.resend_verification()
        if result[1] == 200:
            return render_template('auth/resend_verification.html', success='Email xác thực đã được gửi thành công')
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Gửi lại email xác thực thất bại')
            except:
                error_message = 'Gửi lại email xác thực thất bại'
            return render_template('auth/resend_verification.html', error=error_message)
    return render_template('auth/resend_verification.html')