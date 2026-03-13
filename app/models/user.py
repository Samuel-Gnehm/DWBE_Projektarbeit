import uuid
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))
    vorname = db.Column(db.String(100), nullable=False)
    nachname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwort_hash = db.Column(db.String(255), nullable=False)
    user_rolle = db.Column(db.String(20), nullable=False, default='user')
    status = db.Column(db.String(20), nullable=False, default='active')
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    # Relationships
    scooters = db.relationship('Scooter', backref='provider', lazy=True)
    rides = db.relationship('Ride', backref='rider', lazy=True,
                            foreign_keys='Ride.rider_uid')
    payment_methods = db.relationship('PaymentMethod', backref='rider',
                                      lazy=True)

    # Flask-Login erwartet get_id() → wir geben uid zurück
    def get_id(self):
        return self.uid

    def set_password(self, password):
        self.passwort_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwort_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
