from tests.conftest import login


def test_T08_fahrt_start_ohne_zahlung(client, db, rider, scooter, active_tariff):
    """T08: Rider startet Fahrt ohne Zahlungsmethode – Flash-Fehler, kein Ride in DB."""
    login(client, 'testrider', 'Test1234!')
    response = client.post(f'/rides/start/{scooter.uid}', follow_redirects=True)
    assert response.status_code == 200
    from app.models import Ride
    ride = Ride.query.filter_by(rider_uid=rider.uid).first()
    assert ride is None


def test_T09_fahrt_start_ende_preis(client, db, rider, scooter, active_tariff, payment_method):
    """T09: Fahrt starten und beenden – Preis korrekt, Scooter wieder available."""
    from datetime import datetime, timedelta
    from decimal import Decimal

    login(client, 'testrider', 'Test1234!')

    # Fahrt starten
    client.post(f'/rides/start/{scooter.uid}', follow_redirects=True)

    from app.models import Ride, Scooter as ScooterModel
    ride = Ride.query.filter_by(rider_uid=rider.uid, endzeit=None).first()
    assert ride is not None

    # Scooter ist jetzt rented
    db.session.refresh(scooter)
    assert scooter.status == 'rented'

    # Fahrt beenden mit 10 km
    client.post(f'/rides/end/{ride.uid}', data={
        'gefahrene_km': '10.00'
    }, follow_redirects=True)

    db.session.refresh(ride)
    assert ride.endzeit is not None
    assert ride.gesamtpreis is not None
    # Preis: 2.00 Basispreis + Minuten * 0.25
    assert ride.gesamtpreis >= Decimal('2.00')

    # Scooter ist wieder available
    db.session.refresh(scooter)
    assert scooter.status == 'available'


def test_T10_calculate_price(db, active_tariff):
    """T10: Ride.calculate_price() berechnet Preis korrekt für bekannte Eingabe."""
    from app.models import Ride
    from datetime import datetime
    from decimal import Decimal
    import uuid

    start = datetime(2025, 1, 1, 10, 0, 0)
    end   = datetime(2025, 1, 1, 10, 20, 0)  # exakt 20 Minuten

    ride = Ride(
        rider_uid=str(uuid.uuid4()),
        scooter_uid=str(uuid.uuid4()),
        tarif_uid=active_tariff.uid,
        startzeit=start,
        endzeit=end,
        gefahrene_km=Decimal('5.0')
    )
    ride.tariff = active_tariff  # Relationship manuell setzen für Unit Test
    db.session.add(ride)
    db.session.commit()

    preis = ride.calculate_price()
    # Erwartung: 2.00 + (20 * 0.25) = 7.00
    assert preis == Decimal('7.00')
