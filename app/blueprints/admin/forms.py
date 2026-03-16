from flask_wtf import FlaskForm
from wtforms import DecimalField, DateField, StringField, SelectField, TextAreaField
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
