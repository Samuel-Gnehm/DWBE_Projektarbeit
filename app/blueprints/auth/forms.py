from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from app.models import User


class RegistrationForm(FlaskForm):
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField(
        'Passwort bestätigen',
        validators=[DataRequired(), EqualTo('password', message='Passwörter stimmen nicht überein.')]
    )
    user_rolle = SelectField(
        'Rolle',
        choices=[('user', 'Fahrer'), ('provider', 'Anbieter')],
        validators=[DataRequired()]
    )

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Dieser Benutzername ist bereits vergeben.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Diese E-Mail-Adresse ist bereits registriert.')


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember = BooleanField('Angemeldet bleiben')
