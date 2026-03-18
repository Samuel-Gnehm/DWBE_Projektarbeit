from tests.conftest import login


def test_T06_scooter_anlegen(client, db, provider, vehicle_type):
    """T06: Provider legt neuen Scooter an – erscheint in DB mit Status available."""
    login(client, 'testprovider', 'Test1234!')
    response = client.post('/provider/scooters/add', data={
        'vehicle_type_uid': vehicle_type.uid,
        'model': 'Xiaomi Pro 2',
        'battery_level': 85,
        'latitude': '47.376900',
        'longitude': '8.541700',
        'status': 'available'
    }, follow_redirects=True)
    assert response.status_code == 200
    from app.models import Scooter
    s = Scooter.query.filter_by(model='Xiaomi Pro 2').first()
    assert s is not None
    assert s.status == 'available'
    assert s.qr_code is not None


def test_T07_fremden_scooter_bearbeiten(client, db, provider, provider_b, scooter):
    """T07: Provider B versucht Scooter von Provider A zu bearbeiten – erwartet 403."""
    login(client, 'otherprovider', 'Test1234!')
    response = client.post(f'/provider/scooters/{scooter.uid}/edit', data={
        'model': 'Gehackter Scooter',
        'battery_level': 50,
        'latitude': '47.0',
        'longitude': '8.0',
        'status': 'available'
    })
    assert response.status_code == 403
