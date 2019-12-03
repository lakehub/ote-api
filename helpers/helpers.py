from functools import wraps
import datetime

import jwt
from flask import jsonify, request, current_app

from app.constants import STATUS_USER_DEACTIVATED, STATUS_USER_PENDING
from app.models import User, BlacklistToken


def user_token_required(f):
    """wrapper function for tokens"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = None

        if 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')

        if auth_header:
            auth_token = list(filter(None, auth_header.split(" ")))[1]
        else:
            auth_token = ''

        if not auth_token:
            response = jsonify({'error': True, 'message': 'token is missing!'})
            response.status_code = 401
            return response

        is_token_blacklisted = BlacklistToken.blacklisted(auth_token)

        if is_token_blacklisted:
            response = jsonify({'error': True, 'message': 'Token is blacklisted. Please login again'})
            response.status_code = 401
            return response

        try:
            data = jwt.decode(auth_token, current_app.config['SECRET'], algorithms=['HS256'])
            current_user = User.get_by_public_id(data['public_id'])

            if not current_user:
                response = jsonify({'error': True, 'message': 'token is invalid'})
                response.status_code = 402
                return response

            if current_user.status == STATUS_USER_DEACTIVATED:
                response = jsonify({'error': True, 'message': 'You have been deactivated'})
                response.status_code = 401
                return response

            if current_user.status == STATUS_USER_PENDING:
                response = jsonify({'error': True, 'message': 'Your account is pending'})
                response.status_code = 401
                return response

        except jwt.ExpiredSignatureError:
            response = jsonify({'error': True, 'message': 'token has expired'})
            response.status_code = 401
            return response

        except jwt.InvalidTokenError:
            response = jsonify({'error': True, 'message': 'token is invalid'})
            response.status_code = 401
            return response

        return f(current_user, *args, **kwargs)

    return decorated


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_IMG_EXT']


def create_time(hour, minute):
    """creates time"""
    return datetime.time(hour, minute)
