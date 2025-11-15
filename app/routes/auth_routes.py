from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        result = AuthController.register()
        if result[1] == 201:
            flash('Đăng ký thành công. Vui lòng kiểm tra email để xác thực tài khoản.', 'success')
            return redirect(url_for('auth.login'))
        else:
            # Lấy thông báo lỗi cụ thể từ response
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Đăng ký thất bại')
                flash(error_message, 'error')
            except:
                flash('Đăng ký thất bại', 'error')
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = AuthController.login()
        if result[1] == 200:
            # Lưu token vào session
            try:
                response_data = result[0].get_json()
                if response_data and 'data' in response_data:
                    access_token = response_data['data'].get('access_token')
                    if access_token:
                        session['access_token'] = access_token
            except:
                pass
            
            flash('Đăng nhập thành công', 'success')
            return redirect(url_for('user.profile'))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Đăng nhập thất bại')
                flash(error_message, 'error')
            except:
                flash('Đăng nhập thất bại', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        AuthController.logout()
        # Xóa token khỏi session
        session.pop('access_token', None)
        flash('Đăng xuất thành công', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    result = AuthController.refresh()
    return render_template('auth/refresh.html', result=result)

@auth_bp.route('/verify-token', methods=['GET'])
def verify_token():
    result = AuthController.verify_token()
    return render_template('auth/verify_token.html', result=result)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        result = AuthController.forgot_password()
        flash('Nếu email tồn tại, liên kết đặt lại mật khẩu đã được gửi.', 'info')
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        result = AuthController.reset_password()
        if result[1] == 200:
            flash('Đặt lại mật khẩu thành công', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Đặt lại mật khẩu thất bại', 'error')
    return render_template('auth/reset_password.html')

@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        result = AuthController.verify_email()
        if result[1] == 200:
            flash('Xác thực email thành công', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Xác thực email thất bại', 'error')
    return render_template('auth/verify_email.html')

@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        result = AuthController.resend_verification()
        if result[1] == 200:
            flash('Email xác thực đã được gửi thành công', 'success')
        else:
            flash('Gửi lại email xác thực thất bại', 'error')
    return render_template('auth/resend_verification.html')


