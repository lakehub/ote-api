import datetime

import jwt
from flask import Blueprint, request, jsonify, current_app

from app import bcrypt
from app.constants import ROLE_CUSTOMER, STATUS_USER_DEACTIVATED, STATUS_USER_PENDING, ROLE_RIDER
from app.models import User, BlacklistToken
from helpers.helpers import user_token_required

USERS_BLUEPRINT = Blueprint(name='users', import_name=__name__, url_prefix='/api/v1/user')


@USERS_BLUEPRINT.route('/', methods=['POST'])
def register_customer():
    """"register user"""
    try:
        data = request.get_json()
        name = str(data['name'])
        email = str(data['email'])
        phone_no = str(data['phoneNo'])
        password = str(data['password'])

        if not (name or email or phone_no or password):
            response = jsonify({"error": True, "message": "please, fill all fields"})
            response.status_code = 422
            return response

        email = email.strip()
        name = name.strip()
        phone_no = phone_no.strip()
        phone_no = "+254{}".format(phone_no[1:])

        user = User.get_by_email(email)

        if user:
            response = jsonify({"error": True,
                                "message": "user with email: {} exists".format(email)})
            response.status_code = 409
            return response

        user = User.get_by_phone_no(phone_no)

        if user:
            response = jsonify({"error": True,
                                "message": "user with phone number: 0{} exists".format(phone_no[4:])})
            response.status_code = 409
            return response

        pwd_hash = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(name=name, email=email, phone_no=phone_no, password=pwd_hash, role=ROLE_CUSTOMER)

        user.save()

        response = jsonify({
            "error": False,
            "message": "registration successful",

        })
        response.status_code = 201
        return response
    except KeyError:
        response = jsonify({"error": True, "message": "please, fill all fields"})
        response.status_code = 422
        return response
    except TypeError:
        response = jsonify({"error": True, "message": "data format not JSON"})
        response.status_code = 400
        return response


@USERS_BLUEPRINT.route('/rider', methods=['POST'])
def register_rider():
    """"register rider"""
    try:
        data = request.get_json()
        name = str(data['name'])
        email = str(data['email'])
        phone_no = str(data['phoneNo'])
        password = str(data['password'])
        number_plate = str(data['numberPlate'])
        category = int(data['category'])

        if not (name or email or phone_no or password or number_plate or category):
            response = jsonify({"error": True, "message": "please, fill all fields"})
            response.status_code = 422
            return response

        if category not in range(1, 5):
            response = jsonify({"error": True, "message": "Invalid category"})
            response.status_code = 422
            return response

        email = email.strip()
        name = name.strip()
        phone_no = phone_no.strip()
        phone_no = "+254{}".format(phone_no[1:])

        user = User.get_by_email(email)

        if user:
            response = jsonify({"error": True,
                                "message": "user with email: {} exists".format(email)})
            response.status_code = 409
            return response

        user = User.get_by_phone_no(phone_no)

        if user:
            response = jsonify({"error": True,
                                "message": "user with phone number: 0{} exists".format(phone_no[4:])})
            response.status_code = 409
            return response

        user = User.get_by_number_plate(number_plate)

        if user:
            response = jsonify({"error": True,
                                "message": "number plate exists"})
            response.status_code = 409
            return response

        pwd_hash = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(name=name, email=email, phone_no=phone_no, password=pwd_hash, role=ROLE_RIDER)
        user.number_plate = number_plate
        user.ride_category = category

        user.save()

        response = jsonify({
            "error": False,
            "message": "registration successful",

        })
        response.status_code = 201
        return response
    except KeyError:
        response = jsonify({"error": True, "message": "please, fill all fields"})
        response.status_code = 422
        return response
    except TypeError:
        response = jsonify({"error": True, "message": "data format not JSON"})
        response.status_code = 400
        return response


@USERS_BLUEPRINT.route('/auth/login', methods=['POST'])
def login_user():
    """generate user authorization token"""
    auth = request.authorization

    try:
        if 'Authorization' not in request.headers:
            return jsonify({"error": True, "message": "Please, fill all fields"})

        if not auth.username or not auth.password:
            return jsonify({"error": True, "message": "Please, fill all fields"})

        username = auth.username
        password = auth.password
        username = username.strip()

        if '@' not in username:
            username = "+254{}".format(username[1:])

        user = User.get_by_email_or_phone_no(username)

        if not user:
            response = jsonify({"error": True, "message": "Email, Phone No or password is incorrect"})
            response.status_code = 404
            return response

        if not bcrypt.check_password_hash(user.password, password):
            response = jsonify({"error": True, "message": "Email, Phone No or password is incorrect"})
            response.status_code = 401
            return response

        if user.status == STATUS_USER_DEACTIVATED:
            response = jsonify({"error": True, "message": "You have been deactivated"})
            response.status_code = 401
            return response

        if user.status == STATUS_USER_PENDING:
            response = jsonify({"error": True, "message": "Your registration is pending"})
            response.status_code = 401
            return response

        token = jwt.encode(
            {"public_id": user.public_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)},
            current_app.config['SECRET'], algorithm='HS256')

        return jsonify({
            "error": False,
            "token": token.decode('UTF-8'),
            "details": {
                "name": user.name,
                "email": user.email,
                "phoneNo": user.phone_no,
                "imageUri": user.image_uri
            }
        })

    except KeyError:
        response = jsonify({"error": True, "message": "fill all fields"})
        response.status_code = 422
        return response


@USERS_BLUEPRINT.route('/rider/auth/login', methods=['POST'])
def login_rider():
    """generate user authorization token"""
    auth = request.authorization

    try:
        if 'Authorization' not in request.headers:
            return jsonify({"error": True, "message": "Please, fill all fields"})

        if not auth.username or not auth.password:
            return jsonify({"error": True, "message": "Please, fill all fields"})

        username = auth.username
        password = auth.password
        username = username.strip()

        if '@' not in username:
            username = "+254{}".format(username[1:])

        user = User.get_by_email_or_phone_no(username)

        if not user:
            response = jsonify({"error": True, "message": "Email, Phone No or password is incorrect"})
            response.status_code = 404
            return response

        if not bcrypt.check_password_hash(user.password, password):
            response = jsonify({"error": True, "message": "Email, Phone No or password is incorrect"})
            response.status_code = 401
            return response

        if user.role != ROLE_RIDER:
            response = jsonify({"error": True, "message": "Email, Phone No or password is incorrect"})
            response.status_code = 404
            return response

        if user.status == STATUS_USER_DEACTIVATED:
            response = jsonify({"error": True, "message": "You have been deactivated"})
            response.status_code = 401
            return response

        if user.status == STATUS_USER_PENDING:
            response = jsonify({"error": True, "message": "Your registration is pending"})
            response.status_code = 401
            return response

        token = jwt.encode(
            {"public_id": user.public_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)},
            current_app.config['SECRET'], algorithm='HS256')

        return jsonify({
            "error": False,
            "token": token.decode('UTF-8'),
            "details": {
                "name": user.name,
                "email": user.email,
                "phoneNo": user.phone_no,
                "imageUri": user.image_uri,
                "role": ROLE_RIDER
            }
        })

    except KeyError:
        response = jsonify({"error": True, "message": "fill all fields"})
        response.status_code = 422
        return response


@USERS_BLUEPRINT.route('/auth/validate', methods=['POST'])
def validate_token():
    """validates user token"""
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
        user = User.get_by_public_id(data['public_id'])

        if not user:
            response = jsonify({'error': True, 'message': 'token is invalid'})
            response.status_code = 401
            return response

        if user.status == STATUS_USER_DEACTIVATED:
            response = jsonify({'error': True, 'message': 'You have been deactivated'})
            response.status_code = 401
            return response

        if user.status == STATUS_USER_PENDING:
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

    response = jsonify({"error": False, "message": "token is valid"})
    response.status_code = 200
    return response


@USERS_BLUEPRINT.route('/auth/logout', methods=['POST'])
@user_token_required
def blacklist_auth_token(current_user):
    """blacklist token"""
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
        response = jsonify({'error': True, 'message': 'Token already blacklisted'})
        response.status_code = 401
        return response

    try:
        data = jwt.decode(auth_token, current_app.config['SECRET'], algorithms=['HS256'])
        _current_user = User.get_by_public_id(data['public_id'])

        if not _current_user:
            response = jsonify({'error': True, 'message': 'token is invalid'})
            response.status_code = 401
            return response

        blacklist_token = BlacklistToken(auth_token)
        blacklist_token.save()

        return jsonify({"error": False, "message": "logout successful"})

    except jwt.ExpiredSignatureError:
        response = jsonify({'error': True, 'message': 'token has expired'})
        response.status_code = 401
        return response

    except jwt.InvalidTokenError:
        response = jsonify({'error': True, 'message': 'token is invalid'})
        response.status_code = 401
        return response


@USERS_BLUEPRINT.route('/fcm', methods=['POST', 'PUT'])
@user_token_required
def update_device_id(current_user):
    """creates or updates device registration id"""
    try:
        data = request.get_json()
        device_id = data['deviceId']

        if not device_id:
            response = jsonify({"error": True, "message": "please, fill all fields"})
            response.status_code = 422
            return response

        current_user.device_id = device_id
        current_user.save()

        return jsonify({"error": False, "message": "device id updated successfully"})
    except KeyError:
        response = jsonify({"error": True, "message": "please, fill all fields"})
        response.status_code = 422
        return response
    except TypeError:
        response = jsonify({"error": True, "message": "data format not JSON"})
        response.status_code = 400
        return response


@USERS_BLUEPRINT.route('/location', methods=['POST', 'PUT'])
@user_token_required
def update_location(current_user):
    """creates or updates device registration id"""
    try:
        data = request.get_json()
        lat = data['lat']
        lng = data['lng']

        if not (lng or lat):
            response = jsonify({"error": True, "message": "please, fill all fields"})
            response.status_code = 422
            return response

        current_user.lat = float(lat)
        current_user.lng = float(lng)
        current_user.save()

        return jsonify({"error": False, "message": "device id updated successfully"})
    except KeyError:
        response = jsonify({"error": True, "message": "please, fill all fields"})
        response.status_code = 422
        return response
    except TypeError:
        response = jsonify({"error": True, "message": "data format not JSON"})
        response.status_code = 400
        return response
