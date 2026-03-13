def test_T01_registrierung_gueltig(client, db):
    """T01: Registrierung mit gültigen Daten legt User in DB an."""
    response = client.post('/auth/register', data={
        'vorname': 'Hans',
        'nachname': 'Muster',
        'username': 'hansmuster',
        'email': 'hans@test.ch',
        'password': 'Sicher123!',
        'password_confirm': 'Sicher123!',
        'user_rolle': 'user'
    }, follow_redirects=True)
    assert response.status_code == 200
    from app.models import User
    user = User.query.filter_by(username='hansmuster').first()
    assert user is not None
    assert user.passwort_hash != 'Sicher123!'  # Passwort ist gehasht


def test_T02_login_korrekt(client, db, rider):
    """T02: Login mit korrekten Daten startet Session, Redirect zu /dashboard."""
    response = client.post('/auth/login', data={
        'username': 'testrider',
        'password': 'Test1234!'
    })
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']


def test_T03_login_falsches_passwort(client, db, rider):
    """T03: Login mit falschem Passwort zeigt Fehlermeldung, kein Login."""
    response = client.post('/auth/login', data={
        'username': 'testrider',
        'password': 'FalschesPasswort!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'login' in response.request.path.lower()
