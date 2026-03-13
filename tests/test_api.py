def test_T11_api_login_gibt_token(client, db, rider):
    """T11: POST /api/auth/login mit gültigen Daten gibt JWT-Token zurück."""
    response = client.post('/api/auth/login',
        json={'username': 'testrider', 'password': 'Test1234!'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['token_type'] == 'Bearer'


def test_T12_api_rides_ohne_token(client):
    """T12: GET /api/rides ohne Token gibt 401 mit JSON-Fehlermeldung zurück."""
    response = client.get('/api/rides')
    assert response.status_code == 401
    data = response.get_json()
    assert data is not None  # JSON, nicht HTML
    assert 'error' in data
