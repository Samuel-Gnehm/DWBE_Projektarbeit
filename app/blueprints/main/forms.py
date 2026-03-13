from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class EndRideForm(FlaskForm):
    submit = SubmitField('Fahrt beenden')


class PaymentMethodForm(FlaskForm):
    kartenidentifier_maskiert = StringField(
        'Kartennummer (letzte 4 Stellen oder maskiert, z.B. **** **** **** 1234)',
        validators=[DataRequired(), Length(min=4, max=25)],
    )
    submit = SubmitField('Zahlungsmethode hinzufügen')
