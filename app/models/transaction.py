import uuid
from datetime import datetime

from ..extensions import db


class Transaction(db.Model):
    __tablename__ = 'transactions'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))
    ride_uid = db.Column(db.String(36),
                         db.ForeignKey('rides.uid'), nullable=False)
    payment_method_uid = db.Column(db.String(36),
                                   db.ForeignKey('payment_methods.uid'),
                                   nullable=False)
    betrag = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.uid[:8]} status={self.status}>'
