from datetime import datetime

from flask import Blueprint, request, jsonify, current_app
from pyfcm import FCMNotification

from app.constants import ORDER_CONFIRMED, ORDER_DELIVERY_IN_PROGRESS, ORDER_COMPLETED
from app.models import Order, User
from helpers.helpers import user_token_required

ORDERS_BLUEPRINT = Blueprint(name="orders", import_name=__name__, url_prefix='/api/v1/order')


@ORDERS_BLUEPRINT.route('/', methods=['POST'])
@user_token_required
def place_order(current_user):
    """place order"""
    try:
        data = request.get_json()
        good = data['good']
        time = data['time']
        instructions = data['instructions']
        # preferred = data['preferred']
        fee = int(data['fee'])
        delivery_address = data['deliveryAddress']
        pickup_address = data['pickupAddress']
        delivery_lat = float(data['deliveryLat'])
        delivery_lng = float(data['deliveryLng'])
        pickup_lng = float(data['pickupLng'])
        pickup_lat = float(data['pickupLat'])
        distance = data['distance']
        duration = data['duration']

        if not (
                good or time or instructions or fee, delivery_address, pickup_address, delivery_lng, delivery_lat,
                pickup_lng, pickup_lat, distance, duration):
            response = jsonify({"error": True, "message": "please, fill all fields"})
            response.status_code = 422
            return response

        order = Order(
            good=good,
            instructions=instructions,
            fee=fee,
            delivery_address=delivery_address,
            pickup_address=pickup_address,
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            distance=distance,
            duration=duration
        )
        if time:
            order.date = datetime.strptime(time, "%Y-%m-%d %H:%M")

        order.customer_id = current_user.id
        order.save()

        current_user.orders.append(order)
        current_user.save()

        riders = User.get_riders()

        data_message = {
            "orderId": order.id,
            "deliveryAddress": delivery_address,
            "pickupAddress": pickup_address,
            "good": good,
            "pickupLat": pickup_lat,
            "pickupLng": pickup_lng,
            "deliveryLat": delivery_lat,
            "deliveryLng": delivery_lng,
            "distance": distance,
            "duration": duration,
        }

        device_ids = []
        push_service = FCMNotification(api_key=current_app.config['FCM_API_KEY'])

        for rider in riders:
            if rider.device_id:
                device_ids.append(rider.device_id)

        if len(device_ids) > 0:
            result = push_service.notify_multiple_devices(registration_ids=device_ids, data_message=data_message)

        return jsonify(
            {
                "error": False,
                "message": "order placed successfully",
                "order": {
                    "orderId": order.id,
                    "deliveryAddress": order.delivery_address,
                    "pickupAddress": order.pickup_address,
                    "good": order.good,
                    "pickupLat": order.pickup_lat,
                    "pickupLng": order.pickup_lng,
                    "deliveryLat": order.delivery_lat,
                    "deliveryLng": order.delivery_lng,
                    "distance": order.distance,
                    "duration": order.duration,
                    "fee": order.delivery_fee,
                    "date": order.date.strftime('%Y-%m-%d %H:%M')
                }
            })
    except AttributeError:
        response = jsonify({"error": True, "message": "please, fill all fields"})
        response.status_code = 422
        return response
    except TypeError:
        response = jsonify({"error": True, "message": "data format not JSON"})
        response.status_code = 400
        return response


@ORDERS_BLUEPRINT.route('/<int:order_id>', methods=['POST', 'PUT'])
@user_token_required
def accept_order(current_user, order_id):
    """accept order"""
    order = Order.get_by_id(order_id)

    if not order:
        response = jsonify({"error": True, "message": "order does not exist"})
        response.status_code = 404
        return response

    order.rider_id = current_user.id
    order.users.append(current_user)
    order.status = ORDER_CONFIRMED
    order.save()

    data_message = {
        "messageCategory": 1,
        "orderId": order.id,
        "status": order.status,
        "deliveryAddress": order.delivery_address,
        "pickupAddress": order.pickup_address,
        "good": order.good,
        "pickupLat": order.pickup_lat,
        "pickupLng": order.pickup_lng,
        "deliveryLat": order.delivery_lat,
        "deliveryLng": order.delivery_lng,
        "distance": order.distance,
        "duration": order.duration,
        "fee": order.delivery_fee
    }

    customer = User.get_by_id(order.customer_id)
    push_service = FCMNotification(api_key=current_app.config['FCM_API_KEY'])

    result = push_service.notify_single_device(registration_id=customer.device_id, data_message=data_message)

    return jsonify(
        {
            "error": False, "message":
            "order confirmed successfully",
            "order": {
                "orderId": order.id,
                "deliveryAddress": order.delivery_address,
                "pickupAddress": order.pickup_address,
                "good": order.good,
                "pickupLat": order.pickup_lat,
                "pickupLng": order.pickup_lng,
                "deliveryLat": order.delivery_lat,
                "deliveryLng": order.delivery_lng,
                "distance": order.distance,
                "duration": order.duration,
                "fee": order.delivery_fee,
                "date": order.date.strftime('%Y-%m-%d %H:%M')
            }
        })


@ORDERS_BLUEPRINT.route('/picked/<int:order_id>', methods=['POST', 'PUT'])
@user_token_required
def order_picked(current_user, order_id):
    """order picked"""
    order = Order.get_by_id(order_id)

    if not order:
        response = jsonify({"error": True, "message": "order does not exist"})
        response.status_code = 404
        return response

    order.rider_id = current_user.id
    order.users.append(current_user)
    order.status = ORDER_DELIVERY_IN_PROGRESS
    order.save()

    data_message = {
        "messageCategory": 1,
        "orderId": order.id,
        "status": order.status,
        "deliveryAddress": order.delivery_address,
        "pickupAddress": order.pickup_address,
        "good": order.good,
        "pickupLat": order.pickup_lat,
        "pickupLng": order.pickup_lng,
        "deliveryLat": order.delivery_lat,
        "deliveryLng": order.delivery_lng,
        "distance": order.distance,
        "duration": order.duration,
        "fee": order.delivery_fee
    }

    customer = User.get_by_id(order.customer_id)
    push_service = FCMNotification(api_key=current_app.config['FCM_API_KEY'])

    result = push_service.notify_single_device(registration_id=customer.device_id, data_message=data_message)

    return jsonify(
        {
            "error": False,
            "message": "order picked",
            "order": {
                "orderId": order.id,
                "deliveryAddress": order.delivery_address,
                "pickupAddress": order.pickup_address,
                "good": order.good,
                "pickupLat": order.pickup_lat,
                "pickupLng": order.pickup_lng,
                "deliveryLat": order.delivery_lat,
                "deliveryLng": order.delivery_lng,
                "distance": order.distance,
                "duration": order.duration,
                "fee": order.delivery_fee,
                "date": order.date.strftime('%Y-%m-%d %H:%M')
            }
        })


@ORDERS_BLUEPRINT.route('/completed/<int:order_id>', methods=['POST', 'PUT'])
@user_token_required
def order_completed(current_user, order_id):
    """order completed"""
    order = Order.get_by_id(order_id)

    if not order:
        response = jsonify({"error": True, "message": "order does not exist"})
        response.status_code = 404
        return response

    order.rider_id = current_user.id
    order.users.append(current_user)
    order.status = ORDER_COMPLETED
    order.save()

    data_message = {
        "messageCategory": 1,
        "orderId": order.id,
        "status": order.status,
        "deliveryAddress": order.delivery_address,
        "pickupAddress": order.pickup_address,
        "good": order.good,
        "pickupLat": order.pickup_lat,
        "pickupLng": order.pickup_lng,
        "deliveryLat": order.delivery_lat,
        "deliveryLng": order.delivery_lng,
        "distance": order.distance,
        "duration": order.duration,
        "fee": order.delivery_fee
    }

    customer = User.get_by_id(order.customer_id)
    push_service = FCMNotification(api_key=current_app.config['FCM_API_KEY'])

    result = push_service.notify_single_device(registration_id=customer.device_id, data_message=data_message)

    return jsonify(
        {
            "error": False,
            "message": "order completed",
            "order": {
                "orderId": order.id,
                "deliveryAddress": order.delivery_address,
                "pickupAddress": order.pickup_address,
                "good": order.good,
                "pickupLat": order.pickup_lat,
                "pickupLng": order.pickup_lng,
                "deliveryLat": order.delivery_lat,
                "deliveryLng": order.delivery_lng,
                "distance": order.distance,
                "duration": order.duration,
                "fee": order.delivery_fee,
                "date": order.date.strftime('%Y-%m-%d %H:%M')
            }
        })
