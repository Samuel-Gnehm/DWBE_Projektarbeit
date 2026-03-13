import uuid
from datetime import datetime

from ..extensions import db


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))
    rider_uid = db.Column(db.String(36),
                          db.ForeignKey('users.uid'), nullable=False)
    kartenidentifier_maskiert = db.Column(db.String(25), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='payment_method',
                                   lazy=True)

    def __repr__(self):
        return f'<PaymentMethod {self.kartenidentifier_maskiert}>'
