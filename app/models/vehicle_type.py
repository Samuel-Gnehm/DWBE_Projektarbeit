import uuid

from ..extensions import db


class VehicleType(db.Model):
    __tablename__ = 'vehicle_types'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    # Simulationsparameter (pro Minute)
    meter_per_minute = db.Column(db.Integer, nullable=False, default=200)
    battery_drain_per_minute = db.Column(db.Numeric(5, 2), nullable=False, default=1.0)
    battery_charge_per_minute = db.Column(db.Numeric(5, 2), nullable=False, default=4.0)

    # Relationships
    scooters = db.relationship('Scooter', backref='vehicle_type', lazy=True)
    tariffs = db.relationship('Tariff', backref='vehicle_type', lazy=True)

    @classmethod
    def choices(cls):
        return [(vt.uid, vt.name) for vt in cls.query.order_by(cls.name).all()]

    @classmethod
    def with_active_tariffs(cls):
        from .tariff import Tariff
        types = cls.query.order_by(cls.name).all()
        return [(vt, Tariff.get_active(vt.uid)) for vt in types]

    def __repr__(self):
        return f'<VehicleType {self.name}>'
