from flask import Blueprint
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

auth_bp.route('/register', methods=['POST'])(AuthController.register)
auth_bp.route('/login', methods=['POST'])(AuthController.login)
auth_bp.route('/logout', methods=['POST'])(AuthController.logout)
auth_bp.route('/refresh', methods=['POST'])(AuthController.refresh)
auth_bp.route('/verify-token', methods=['GET'])(AuthController.verify_token)
auth_bp.route('/forgot-password', methods=['POST'])(AuthController.forgot_password)
auth_bp.route('/reset-password', methods=['POST'])(AuthController.reset_password)
auth_bp.route('/verify-email', methods=['POST'])(AuthController.verify_email)
auth_bp.route('/resend-verification', methods=['POST'])(AuthController.resend_verification)


