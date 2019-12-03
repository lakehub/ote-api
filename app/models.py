import datetime
import time

from sqlalchemy import or_

from app import db
from app.constants import STATUS_USER_PENDING, STATUS_USER_ACTIVE, ROLE_RIDER, ORDER_WAITING_CONFIRMATION

user_order_assoc = db.Table(
    'user_order_assoc',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'))
)


class User(db.Model):
    """Users Model"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.BigInteger)
    email = db.Column(db.Unicode(255), unique=True)
    phone_no = db.Column(db.String(13), unique=True)
    name = db.Column(db.String(255))
    status = db.Column(db.Integer)
    role = db.Column(db.Integer)
    password = db.Column(db.Unicode(255))
    image_uri = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    number_plate = db.Column(db.String(50))
    device_id = db.Column(db.VARCHAR(255))
    ride_category = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    orders = db.relationship('Order', secondary=user_order_assoc)
    current_status = db.Column(db.Integer)

    def __init__(self, email, phone_no, name, password, role):
        self.name = name
        self.email = email
        self.phone_no = phone_no
        self.password = password
        self.role = role
        self.status = STATUS_USER_ACTIVE
        self.public_id = str(int(time.mktime(datetime.datetime.utcnow().timetuple())))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<User: {}>".format(self.phone_no)

    @staticmethod
    def get_by_email(email):
        """get user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_phone_no(phone_no):
        """get user by phone no"""
        return User.query.filter_by(phone_no=phone_no).first()

    @staticmethod
    def get_by_public_id(public_id):
        """get user by public id"""
        return User.query.filter_by(public_id=public_id).first()

    @staticmethod
    def get_by_id(user_id):
        """get user by public id"""
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_riders():
        """get user by public id"""
        return User.query.filter_by(role=ROLE_RIDER).all()

    @staticmethod
    def get_all():
        """get all users"""
        return User.query.all()

    @staticmethod
    def get_by_email_or_phone_no(value):
        return User.query.filter(or_(User.phone_no == value, User.email == value)).first()

    @staticmethod
    def get_by_number_plate(number_plate):
        """get user by number plate"""
        return User.query.filter_by(number_plate=number_plate).first()


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT blacklisted tokens
    """
    __tablename__ = 'blacklist_tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, token):
        self.token = token

    def save(self):
        """creates blacklisted token"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def blacklisted(token):
        """test if the token is blacklisted"""
        return BlacklistToken.query.filter_by(token=token).first()

    def __repr__(self):
        return '<Token: {}'.format(self.token)


class Order(db.Model):
    """Orders Model"""
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    good = db.Column(db.String(250))
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    instructions = db.Column(db.String(250))
    users = db.relationship('User', secondary=user_order_assoc)
    status = db.Column(db.Integer, default=ORDER_WAITING_CONFIRMATION)
    pickup_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    delivery_fee = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    pickup_lat = db.Column(db.Float)
    pickup_lng = db.Column(db.Float)
    delivery_lat = db.Column(db.Float)
    delivery_lng = db.Column(db.Float)
    delivery_address = db.Column(db.String(250))
    pickup_address = db.Column(db.String(250))
    distance = db.Column(db.BigInteger)
    duration = db.Column(db.BigInteger)
    rider_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)

    def __init__(self, good, instructions, fee, pickup_lat, pickup_lng, delivery_lat, delivery_lng, pickup_address,
                 delivery_address, distance, duration):
        self.good = good
        self.instructions = instructions
        self.delivery_fee = fee
        self.delivery_lat = delivery_lat
        self.delivery_lng = delivery_lng
        self.pickup_lat = pickup_lat
        self.pickup_lng = pickup_lng
        self.pickup_address = pickup_address
        self.delivery_address = delivery_address
        self.distance = distance
        self.duration = duration

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Order: {}>".format(self.good)

    @staticmethod
    def get_by_id(order_id):
        """get order by id"""
        return Order.query.filter_by(id=order_id).first()
