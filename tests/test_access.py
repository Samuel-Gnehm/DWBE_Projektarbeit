from tests.conftest import login


def test_T04_rider_auf_provider_route(client, db, rider):
    """T04: Rider ruft /provider/scooters auf – erwartet 403."""
    login(client, 'testrider', 'Test1234!')
    response = client.get('/provider/scooters')
    assert response.status_code == 403


def test_T05_nicht_eingeloggt_dashboard(client):
    """T05: Nicht eingeloggter User ruft /dashboard auf – Redirect zu /auth/login."""
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']
