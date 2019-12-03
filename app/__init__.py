from flask import jsonify
from flask.debughelpers import FormDataRoutingRedirect
from flask_api import FlaskAPI
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from instance.config import app_config

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    @app.errorhandler(400)
    def bad_request(error):
        response = jsonify({"error": True, "message": "bad request"})
        response.status_code = 400
        return response

    @app.errorhandler(404)
    def not_found(error):
        response = jsonify({"error": True, "message": "resource not found"})
        response.status_code = 404
        return response

    @app.errorhandler(405)
    def method_not_allowed(error):
        response = jsonify({"error": True, "message": "method not allowed"})
        response.status_code = 405
        return response

    @app.errorhandler(500)
    def server_error(error):
        response = jsonify({"error": True, "message": "internal server error"})
        response.status_code = 500
        return response

    @app.errorhandler(FormDataRoutingRedirect)
    def handle_routing_error(error):
        """handle trailing slash error"""
        response = jsonify({"error": True, "message": "resource not found"})
        response.status_code = 404
        return response

    from app.users.Users import USERS_BLUEPRINT
    from app.orders.Orders import ORDERS_BLUEPRINT

    app.register_blueprint(USERS_BLUEPRINT)
    app.register_blueprint(ORDERS_BLUEPRINT)

    return app
