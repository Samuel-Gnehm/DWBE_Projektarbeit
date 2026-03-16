import uuid
from datetime import datetime

from ..extensions import db


class Ride(db.Model):
    __tablename__ = 'rides'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))
    rider_uid = db.Column(db.String(36),
                          db.ForeignKey('users.uid'), nullable=False)
    scooter_uid = db.Column(db.String(36),
                            db.ForeignKey('scooters.uid'), nullable=False)
    tarif_uid = db.Column(db.String(36),
                          db.ForeignKey('tariffs.uid'), nullable=False)
    startzeit = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow)
    endzeit = db.Column(db.DateTime, nullable=True)   # NULL = Fahrt aktiv
    gesamtpreis = db.Column(db.Numeric(10, 2), nullable=True)
    gefahrene_km = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    # Relationships
    transaction = db.relationship('Transaction', backref='ride',
                                  uselist=False, lazy=True)

    @classmethod
    def get_active_for(cls, user_uid):
        return cls.query.filter_by(rider_uid=user_uid, endzeit=None).first()

    @property
    def duration_str(self):
        from datetime import datetime
        end = self.endzeit or datetime.utcnow()
        total = int((end - self.startzeit).total_seconds())
        return f'{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}'

    def calculate_price(self):
        """Berechnet den Gesamtpreis der Fahrt: Basispreis + (Minutenpreis × Minuten)."""
        from decimal import Decimal
        if self.endzeit is None or self.startzeit is None:
            return None
        dauer_sekunden = (self.endzeit - self.startzeit).total_seconds()
        minuten = Decimal(str(round(dauer_sekunden / 60, 2)))
        preis = self.tariff.base_price + (self.tariff.minute_price * minuten)
        return round(preis, 2)

    def to_dict(self):
        return {
            'uid': self.uid,
            'rider_uid': self.rider_uid,
            'scooter_uid': self.scooter_uid,
            'tarif_uid': self.tarif_uid,
            'startzeit': self.startzeit.isoformat() if self.startzeit else None,
            'endzeit': self.endzeit.isoformat() if self.endzeit else None,
            'gesamtpreis': float(self.gesamtpreis) if self.gesamtpreis else None,
            'gefahrene_km': float(self.gefahrene_km or 0),
        }

    def __repr__(self):
        return f'<Ride {self.uid[:8]} rider={self.rider_uid[:8]}>'
