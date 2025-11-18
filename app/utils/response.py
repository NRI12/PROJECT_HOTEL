from flask import jsonify

def success_response(data=None, message='Success', status_code=200):
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message='Error', status_code=400, errors=None):
    response = {
        'success': False,
        'message': message
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code

def validation_error_response(errors):
    error_messages = []
    if isinstance(errors, dict):
        for field, messages in errors.items():
            if isinstance(messages, list):
                for msg in messages:
                    error_messages.append(f"{field}: {msg}")
            else:
                error_messages.append(f"{field}: {messages}")
    else:
        error_messages.append(str(errors))
    
    return error_response(
        message='; '.join(error_messages),
        status_code=400,
        errors=errors
    )

def paginated_response(items, page, per_page, total, message='Success'):
    return jsonify({
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200