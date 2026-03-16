from flask_wtf import FlaskForm
from wtforms import DecimalField, DateField, IntegerField, StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional


class TariffForm(FlaskForm):
    vehicle_type_uid = SelectField(
        'Fahrzeugtyp',
        validators=[DataRequired(message='Bitte einen Fahrzeugtyp wählen.')],
    )
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


class VehicleTypeForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=100)]
    )
    description = TextAreaField(
        'Beschreibung',
        validators=[Optional(), Length(max=255)]
    )
    meter_per_minute = IntegerField(
        'Meter / Minute',
        validators=[DataRequired(), NumberRange(min=1, max=10000)]
    )
    battery_drain_per_minute = DecimalField(
        'Akku-Verbrauch % / Minute (Fahrt)',
        places=2,
        validators=[DataRequired(), NumberRange(min=0.01, max=100)]
    )
    battery_charge_per_minute = DecimalField(
        'Akku-Laden % / Minute (Wartung)',
        places=2,
        validators=[DataRequired(), NumberRange(min=0.01, max=100)]
    )
