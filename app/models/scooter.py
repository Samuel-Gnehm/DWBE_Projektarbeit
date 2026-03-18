import uuid
from datetime import datetime

from ..extensions import db


class Scooter(db.Model):
    __tablename__ = 'scooters'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))
    uid_provider = db.Column(db.String(36),
                             db.ForeignKey('users.uid'), nullable=False)
    vehicle_type_uid = db.Column(db.String(36),
                                 db.ForeignKey('vehicle_types.uid'), nullable=True)
    model = db.Column(db.String(100), nullable=False)
    qr_code = db.Column(db.String(100), unique=True, nullable=False,
                        default=lambda: str(uuid.uuid4()))
    status = db.Column(db.String(20), nullable=False, default='available')
    gefahrene_km_gesamt = db.Column(db.Numeric(10, 2), nullable=False,
                                    default=0)
    battery_level = db.Column(db.SmallInteger, nullable=False, default=100)
    maintenance_since = db.Column(db.DateTime, nullable=True)
    latitude = db.Column(db.Numeric(9, 6), nullable=True)
    longitude = db.Column(db.Numeric(9, 6), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    # Relationships
    rides = db.relationship('Ride', backref='scooter', lazy=True)

    def to_dict(self):
        return {
            'uid': self.uid,
            'model': self.model,
            'qr_code': self.qr_code,
            'status': self.status,
            'gefahrene_km_gesamt': float(self.gefahrene_km_gesamt or 0),
            'battery_level': self.battery_level,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'vehicle_type_uid': self.vehicle_type_uid,
            'vehicle_type_name': self.vehicle_type.name if self.vehicle_type else None,
        }

    def __repr__(self):
        return f'<Scooter {self.model} ({self.status})>'
