from flask import request, session
from contextlib import contextmanager

@contextmanager
def jwt_token_from_session():
    """Context manager để inject token từ session vào request"""
    if 'access_token' in session:
        token = session.get('access_token')
        if token:
            # Lưu header hiện tại nếu có
            original_auth = request.headers.get('Authorization')
            # Set token vào request environment
            request.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'
            try:
                yield
            finally:
                # Khôi phục header ban đầu nếu có
                if original_auth:
                    request.environ['HTTP_AUTHORIZATION'] = original_auth
                elif 'HTTP_AUTHORIZATION' in request.environ:
                    del request.environ['HTTP_AUTHORIZATION']
        else:
            yield
    else:
        yield

