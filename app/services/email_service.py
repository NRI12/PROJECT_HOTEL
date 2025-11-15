from flask_mail import Message
from app import mail
from flask import current_app, render_template_string
import threading

class EmailService:
    
    @staticmethod
    def send_email(to, subject, body, html=None):
        try:
            msg = Message(
                subject=subject,
                recipients=[to],
                body=body,
                html=html,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    @staticmethod
    def send_email_async(to, subject, body, html=None):
        app = current_app._get_current_object()
        
        def send():
            with app.app_context():
                try:
                    msg = Message(
                        subject=subject,
                        recipients=[to],
                        body=body,
                        html=html,
                        sender=app.config['MAIL_DEFAULT_SENDER']
                    )
                    mail.send(msg)
                except Exception as e:
                    print(f"Error sending email async: {str(e)}")
        
        thread = threading.Thread(target=send)
        thread.daemon = True
        thread.start()
        return True
    
    @staticmethod
    def send_verification_email(user, token, async_send=True):
        verification_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:8000')}/auth/verify-email.html?token={token}"
        
        subject = 'Xác thực email của bạn'
        body = f'''
        Xin chào {user.full_name},
        
        Vui lòng click vào link dưới đây để xác thực email của bạn:
        {verification_url}
        
        Link này sẽ hết hạn sau 24 giờ.
        
        Nếu bạn không yêu cầu xác thực này, vui lòng bỏ qua email này.
        
        Trân trọng,
        Hotel Booking Team
        '''
        
        html = f'''
        <html>
            <body>
                <h2>Xác thực email</h2>
                <p>Xin chào {user.full_name},</p>
                <p>Vui lòng click vào nút dưới đây để xác thực email của bạn:</p>
                <a href="{verification_url}" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Xác thực Email</a>
                <p>Hoặc copy link sau vào trình duyệt:</p>
                <p>{verification_url}</p>
                <p>Link này sẽ hết hạn sau 24 giờ.</p>
                <p>Nếu bạn không yêu cầu xác thực này, vui lòng bỏ qua email này.</p>
                <br>
                <p>Trân trọng,<br>Hotel Booking Team</p>
            </body>
        </html>
        '''
        
        if async_send:
            return EmailService.send_email_async(user.email, subject, body, html)
        else:
            return EmailService.send_email(user.email, subject, body, html)
    
    @staticmethod
    def send_reset_password_email(user, token, async_send=True):
        reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:8000')}/auth/reset-password.html?token={token}"
        
        subject = 'Đặt lại mật khẩu'
        body = f'''
        Xin chào {user.full_name},
        
        Chúng tôi đã nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.
        
        Vui lòng click vào link dưới đây để đặt lại mật khẩu:
        {reset_url}
        
        Link này sẽ hết hạn sau 1 giờ.
        
        Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
        
        Trân trọng,
        Hotel Booking Team
        '''
        
        html = f'''
        <html>
            <body>
                <h2>Đặt lại mật khẩu</h2>
                <p>Xin chào {user.full_name},</p>
                <p>Chúng tôi đã nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                <p>Vui lòng click vào nút dưới đây để đặt lại mật khẩu:</p>
                <a href="{reset_url}" style="display: inline-block; padding: 10px 20px; background-color: #FF5722; color: white; text-decoration: none; border-radius: 5px;">Đặt lại mật khẩu</a>
                <p>Hoặc copy link sau vào trình duyệt:</p>
                <p>{reset_url}</p>
                <p>Link này sẽ hết hạn sau 1 giờ.</p>
                <p>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.</p>
                <br>
                <p>Trân trọng,<br>Hotel Booking Team</p>
            </body>
        </html>
        '''
        
        if async_send:
            return EmailService.send_email_async(user.email, subject, body, html)
        else:
            return EmailService.send_email(user.email, subject, body, html)


