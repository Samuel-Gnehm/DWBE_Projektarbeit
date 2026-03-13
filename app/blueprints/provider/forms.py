from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField, DateField
from wtforms.validators import DataRequired, Length, NumberRange


class ScooterForm(FlaskForm):
    model = StringField(
        'Modellbezeichnung',
        validators=[DataRequired(), Length(max=100)]
    )
    battery_level = IntegerField(
        'Akkustand (%)',
        validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    latitude = DecimalField(
        'Breitengrad (Latitude)',
        validators=[DataRequired(), NumberRange(min=-90, max=90, message='Breitengrad muss zwischen -90 und 90 liegen.')],
        places=6
    )
    longitude = DecimalField(
        'Längengrad (Longitude)',
        validators=[DataRequired(), NumberRange(min=-180, max=180, message='Längengrad muss zwischen -180 und 180 liegen.')],
        places=6
    )
    status = SelectField(
        'Status',
        choices=[
            ('available', 'Verfügbar'),
            ('maintenance', 'In Wartung'),
            ('disabled', 'Deaktiviert'),
        ]
    )


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
