# Aufruf: python seed.py
from app import create_app
from app.extensions import db
from app.models import User
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))

with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin = User(
            vorname='Admin',
            nachname='Admin',
            username='admin',
            email='admin@escooter.local',
            user_rolle='admin',
            status='active'
        )
        admin.set_password('Admin1234!')
        db.session.add(admin)
        db.session.commit()
        print("Admin-User erstellt: admin / Admin1234!")
    else:
        print("Admin-User existiert bereits.")
