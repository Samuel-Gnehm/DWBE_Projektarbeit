import uuid

from ..extensions import db


class Tariff(db.Model):
    __tablename__ = 'tariffs'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))
    vehicle_type_uid = db.Column(db.String(36),
                                 db.ForeignKey('vehicle_types.uid'), nullable=True)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    minute_price = db.Column(db.Numeric(10, 2), nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=True)   # NULL = aktuell aktiv
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    rides = db.relationship('Ride', backref='tariff', lazy=True)

    @classmethod
    def get_active(cls, vehicle_type_uid=None):
        """Gibt den aktiven Tarif für den angegebenen Fahrzeugtyp zurück.
        Ohne vehicle_type_uid wird der globale aktive Tarif (ohne Typ) zurückgegeben."""
        return cls.query.filter_by(is_active=True, vehicle_type_uid=vehicle_type_uid).first()

    def __repr__(self):
        return f'<Tariff base={self.base_price} min={self.minute_price}>'
