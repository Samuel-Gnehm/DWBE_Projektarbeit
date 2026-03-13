import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User, Scooter, Tariff, PaymentMethod


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'JWT_SECRET_KEY': 'test-secret'
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Committed Daten nach jedem Test bereinigen
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def rider(db):
    """Erstellt einen Rider-User für Tests."""
    u = User(
        vorname='Test', nachname='Rider',
        username='testrider', email='rider@test.ch',
        user_rolle='user', status='active'
    )
    u.set_password('Test1234!')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture(scope='function')
def provider(db):
    """Erstellt einen Provider-User für Tests."""
    u = User(
        vorname='Test', nachname='Provider',
        username='testprovider', email='provider@test.ch',
        user_rolle='provider', status='active'
    )
    u.set_password('Test1234!')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture(scope='function')
def provider_b(db):
    """Zweiter Provider für Zugriffsschutz-Tests."""
    u = User(
        vorname='Other', nachname='Provider',
        username='otherprovider', email='other@test.ch',
        user_rolle='provider', status='active'
    )
    u.set_password('Test1234!')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture(scope='function')
def scooter(db, provider):
    """Erstellt einen Scooter für Provider."""
    import uuid
    s = Scooter(
        uid_provider=provider.uid,
        model='TestScooter X1',
        qr_code=str(uuid.uuid4()),
        status='available',
        battery_level=80,
        latitude=47.3769,
        longitude=8.5417,
        gefahrene_km_gesamt=0.0
    )
    db.session.add(s)
    db.session.commit()
    return s


@pytest.fixture(scope='function')
def active_tariff(db):
    """Erstellt einen aktiven Tarif."""
    from datetime import date
    t = Tariff(
        base_price=2.00,
        minute_price=0.25,
        valid_from=date.today(),
        valid_to=None,
        is_active=True
    )
    db.session.add(t)
    db.session.commit()
    return t


@pytest.fixture(scope='function')
def payment_method(db, rider):
    """Erstellt eine aktive Zahlungsmethode für den Rider."""
    pm = PaymentMethod(
        rider_uid=rider.uid,
        kartenidentifier_maskiert='**** **** **** 1234',
        is_active=True
    )
    db.session.add(pm)
    db.session.commit()
    return pm


def login(client, username, password):
    """Hilfsfunktion: User per Session einloggen."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)
