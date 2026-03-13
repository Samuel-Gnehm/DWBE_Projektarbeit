from flask_wtf import FlaskForm
from wtforms import DecimalField, DateField
from wtforms.validators import DataRequired, NumberRange


class TariffForm(FlaskForm):
    base_price = DecimalField(
        'Basispreis (CHF)',
        validators=[DataRequired(), NumberRange(min=0)],
        places=2
    )
    minute_price = DecimalField(
        'Preis pro Minute (CHF)',
        validators=[DataRequired(), NumberRange(min=0)],
        places=2
    )
    valid_from = DateField(
        'Gültig ab',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
