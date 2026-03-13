import uuid
from datetime import datetime
from decimal import Decimal

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from . import api_bp
from app.extensions import db
from app.models import User, Scooter, Ride, Tariff, Transaction


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'username und password erforderlich'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Ungültige Anmeldedaten'}), 401

    if user.status != 'active':
        return jsonify({'error': 'Account deaktiviert'}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_access_token(
        identity=user.uid,
        additional_claims={'rolle': user.user_rolle}
    )
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'rolle': user.user_rolle,
        'username': user.username
    }), 200


# ---------------------------------------------------------------------------
# GET /api/scooters  –  public
# ---------------------------------------------------------------------------

@api_bp.route('/scooters', methods=['GET'])
def api_get_scooters():
    scooters = Scooter.query.filter_by(status='available').all()
    return jsonify([s.to_dict() for s in scooters]), 200


# ---------------------------------------------------------------------------
# GET /api/scooters/<uid>  –  public
# ---------------------------------------------------------------------------

@api_bp.route('/scooters/<uid>', methods=['GET'])
def api_get_scooter(uid):
    scooter = Scooter.query.get(uid)
    if not scooter:
        return jsonify({'error': 'Scooter nicht gefunden'}), 404
    return jsonify(scooter.to_dict()), 200


# ---------------------------------------------------------------------------
# POST /api/scooters  –  JWT (Provider)
# ---------------------------------------------------------------------------

@api_bp.route('/scooters', methods=['POST'])
@jwt_required()
def api_create_scooter():
    claims = get_jwt()
    if claims.get('rolle') != 'provider':
        return jsonify({'error': 'Nur Provider dürfen Scooter anlegen'}), 403

    data = request.get_json()
    required = ['model', 'battery_level', 'latitude', 'longitude']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Pflichtfeld fehlt: {field}'}), 400

    scooter = Scooter(
        uid_provider=get_jwt_identity(),
        model=data['model'],
        qr_code=str(uuid.uuid4()),
        status='available',
        battery_level=int(data['battery_level']),
        latitude=Decimal(str(data['latitude'])),
        longitude=Decimal(str(data['longitude'])),
        gefahrene_km_gesamt=Decimal('0.0')
    )
    db.session.add(scooter)
    db.session.commit()
    return jsonify(scooter.to_dict()), 201


# ---------------------------------------------------------------------------
# GET /api/rides  –  JWT (Rider)
# ---------------------------------------------------------------------------

@api_bp.route('/rides', methods=['GET'])
@jwt_required()
def api_get_rides():
    uid = get_jwt_identity()
    rides = (
        Ride.query
        .filter(Ride.rider_uid == uid, Ride.endzeit != None)  # noqa: E711
        .order_by(Ride.startzeit.desc())
        .all()
    )
    return jsonify([r.to_dict() for r in rides]), 200


# ---------------------------------------------------------------------------
# GET /api/rides/<uid>  –  JWT (Rider)
# ---------------------------------------------------------------------------

@api_bp.route('/rides/<uid>', methods=['GET'])
@jwt_required()
def api_get_ride(uid):
    current_uid = get_jwt_identity()
    ride = Ride.query.get(uid)
    if not ride:
        return jsonify({'error': 'Fahrt nicht gefunden'}), 404
    if ride.rider_uid != current_uid:
        return jsonify({'error': 'Zugriff verweigert'}), 403
    return jsonify(ride.to_dict()), 200


# ---------------------------------------------------------------------------
# GET /api/tariffs/active  –  public
# ---------------------------------------------------------------------------

@api_bp.route('/tariffs/active', methods=['GET'])
def api_get_active_tariff():
    tariff = Tariff.get_active()
    if not tariff:
        return jsonify({'error': 'Kein aktiver Tarif vorhanden'}), 404
    return jsonify({
        'uid': tariff.uid,
        'base_price': float(tariff.base_price),
        'minute_price': float(tariff.minute_price),
        'valid_from': tariff.valid_from.isoformat() if tariff.valid_from else None
    }), 200


# ---------------------------------------------------------------------------
# GET /api/transactions  –  JWT (Rider)
# ---------------------------------------------------------------------------

@api_bp.route('/transactions', methods=['GET'])
@jwt_required()
def api_get_transactions():
    uid = get_jwt_identity()
    transactions = (
        Transaction.query
        .join(Ride, Transaction.ride_uid == Ride.uid)
        .filter(Ride.rider_uid == uid)
        .order_by(Transaction.created_at.desc())
        .all()
    )
    return jsonify([{
        'uid': t.uid,
        'ride_uid': t.ride_uid,
        'betrag': float(t.betrag),
        'status': t.status,
        'created_at': t.created_at.isoformat() if t.created_at else None
    } for t in transactions]), 200
