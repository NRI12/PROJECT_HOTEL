from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from jwt.exceptions import InvalidTokenError
from flask_jwt_extended.exceptions import NoAuthorizationError

def register_error_handlers(app):
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            'success': False,
            'message': e.description,
            'error': e.name
        }), e.code
    
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        return jsonify({
            'success': False,
            'data': None,
            'message': 'Missing or invalid authorization token',
            'error': 'Unauthorized'
        }), 401
    
    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token_error(e):
        return jsonify({
            'success': False,
            'data': None,
            'message': 'Invalid token',
            'error': 'Unauthorized'
        }), 401
    
    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500
    
    @app.errorhandler(Exception)
    def handle_generic_error(e):
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500


