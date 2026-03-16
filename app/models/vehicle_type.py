import uuid

from ..extensions import db


class VehicleType(db.Model):
    __tablename__ = 'vehicle_types'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    scooters = db.relationship('Scooter', backref='vehicle_type', lazy=True)
    tariffs = db.relationship('Tariff', backref='vehicle_type', lazy=True)

    def __repr__(self):
        return f'<VehicleType {self.name}>'
