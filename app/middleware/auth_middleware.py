from flask import session

def configure_jwt_callbacks(jwt):
    """Configure JWT callbacks to support session-based token storage"""

    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        return {'user_id': identity}

    @jwt.user_lookup_error_loader
    def custom_user_lookup_error(jwt_header, jwt_payload):
        return {
            'success': False,
            'error': 'User not found',
            'message': 'User associated with this token no longer exists',
            'data': None
        }, 404


class SessionTokenMiddleware:
    """WSGI middleware to inject JWT token from Flask session into request headers"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # We can't access Flask session here as it's not available in WSGI layer
        # This middleware serves as a placeholder for future WSGI-level auth
        return self.app(environ, start_response)
