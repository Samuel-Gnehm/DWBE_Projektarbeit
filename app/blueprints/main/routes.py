from datetime import datetime
from decimal import Decimal

from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.ride import Ride
from app.models.scooter import Scooter
from app.models.tariff import Tariff
from app.models.payment_method import PaymentMethod
from app.models.transaction import Transaction
from app.utils import rider_required

from . import main_bp
from .forms import EndRideForm, PaymentMethodForm


# ---------------------------------------------------------------------------
# Index / Redirect
# ---------------------------------------------------------------------------

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        role = current_user.user_rolle
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'provider':
            return redirect(url_for('provider.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


# ---------------------------------------------------------------------------
# Rider Dashboard
# ---------------------------------------------------------------------------

@main_bp.route('/dashboard')
@login_required
@rider_required
def dashboard():
    active_ride = Ride.query.filter_by(
        rider_uid=current_user.uid, endzeit=None
    ).first()
    completed_count = Ride.query.filter(
        Ride.rider_uid == current_user.uid,
        Ride.endzeit != None  # noqa: E711
    ).count()
    active_payment = PaymentMethod.query.filter_by(
        rider_uid=current_user.uid, is_active=True
    ).first()
    return render_template(
        'main/dashboard.html',
        active_ride=active_ride,
        completed_count=completed_count,
        active_payment=active_payment,
    )


# ---------------------------------------------------------------------------
# Scooter-Liste
# ---------------------------------------------------------------------------

@main_bp.route('/scooters')
@login_required
@rider_required
def scooters():
    available_scooters = Scooter.query.filter_by(status='available').all()
    active_ride = Ride.query.filter_by(
        rider_uid=current_user.uid, endzeit=None
    ).first()
    return render_template(
        'main/scooters.html',
        scooters=available_scooters,
        active_ride=active_ride,
    )


# ---------------------------------------------------------------------------
# Fahrt starten
# ---------------------------------------------------------------------------

@main_bp.route('/rides/start/<scooter_uid>', methods=['POST'])
@login_required
@rider_required
def ride_start(scooter_uid):
    scooter = Scooter.query.get_or_404(scooter_uid)

    if scooter.status != 'available':
        flash('Dieser Scooter ist nicht verfügbar.', 'warning')
        return redirect(url_for('main.scooters'))

    active_ride = Ride.query.filter_by(
        rider_uid=current_user.uid, endzeit=None
    ).first()
    if active_ride:
        flash('Du hast bereits eine aktive Fahrt.', 'warning')
        return redirect(url_for('main.ride_active'))

    payment = PaymentMethod.query.filter_by(
        rider_uid=current_user.uid, is_active=True
    ).first()
    if not payment:
        flash('Bitte hinterlege zuerst eine Zahlungsmethode.', 'warning')
        return redirect(url_for('main.payment_methods'))

    tariff = Tariff.get_active(vehicle_type_uid=scooter.vehicle_type_uid)
    if not tariff:
        flash('Kein aktiver Tarif für diesen Fahrzeugtyp vorhanden. Bitte Administrator kontaktieren.', 'danger')
        return redirect(url_for('main.scooters'))

    ride = Ride(
        rider_uid=current_user.uid,
        scooter_uid=scooter.uid,
        tarif_uid=tariff.uid,
        startzeit=datetime.utcnow(),
        endzeit=None,
        gesamtpreis=None,
        gefahrene_km=0.0,
    )
    scooter.status = 'rented'
    db.session.add(ride)
    db.session.commit()
    flash('Fahrt gestartet! Gute Fahrt 🛴', 'success')
    return redirect(url_for('main.ride_active'))


# ---------------------------------------------------------------------------
# Aktive Fahrt anzeigen
# ---------------------------------------------------------------------------

@main_bp.route('/rides/active')
@login_required
@rider_required
def ride_active():
    ride = Ride.query.filter_by(
        rider_uid=current_user.uid, endzeit=None
    ).first()
    if not ride:
        flash('Keine aktive Fahrt.', 'info')
        return redirect(url_for('main.scooters'))

    now = datetime.utcnow()
    duration = now - ride.startzeit
    tariff = ride.tariff
    minuten = (now - ride.startzeit).total_seconds() / 60
    vorschau = tariff.base_price + (tariff.minute_price * Decimal(str(round(minuten, 2))))
    vorschau = round(vorschau, 2)

    total_seconds = int(duration.total_seconds())
    duration_str = f'{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}'

    return render_template(
        'main/active_ride.html',
        ride=ride,
        scooter=ride.scooter,
        tariff=tariff,
        duration_str=duration_str,
        vorschau=vorschau,
    )


# ---------------------------------------------------------------------------
# Fahrt beenden
# ---------------------------------------------------------------------------

@main_bp.route('/rides/end/<ride_uid>', methods=['GET', 'POST'])
@login_required
@rider_required
def ride_end(ride_uid):
    ride = Ride.query.get_or_404(ride_uid)
    if ride.rider_uid != current_user.uid:
        abort(403)
    if ride.endzeit is not None:
        flash('Diese Fahrt ist bereits beendet.', 'info')
        return redirect(url_for('main.ride_history'))

    form = EndRideForm()
    if form.validate_on_submit():
        ride.endzeit = datetime.utcnow()
        minuten = (ride.endzeit - ride.startzeit).total_seconds() / 60
        ride.gefahrene_km = Decimal(str(round(minuten * 0.2, 3)))
        ride.gesamtpreis = ride.calculate_price()

        scooter = ride.scooter
        scooter.status = 'available'
        scooter.gefahrene_km_gesamt += ride.gefahrene_km
        scooter.battery_level = max(0, scooter.battery_level - int(minuten))
        try:
            drop_lat = request.form.get('drop_lat')
            drop_lng = request.form.get('drop_lng')
            if drop_lat and drop_lng:
                scooter.latitude = Decimal(drop_lat)
                scooter.longitude = Decimal(drop_lng)
        except Exception:
            pass

        payment = PaymentMethod.query.filter_by(
            rider_uid=current_user.uid, is_active=True
        ).first()
        transaction = Transaction(
            ride_uid=ride.uid,
            payment_method_uid=payment.uid,
            betrag=ride.gesamtpreis,
            status='completed',
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Fahrt beendet. Kosten: CHF {ride.gesamtpreis:.2f}', 'success')
        return redirect(url_for('main.ride_detail', ride_uid=ride.uid))

    now = datetime.utcnow()
    duration = now - ride.startzeit
    total_seconds = int(duration.total_seconds())
    duration_str = f'{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}'

    return render_template(
        'main/end_ride.html',
        ride=ride,
        scooter=ride.scooter,
        form=form,
        duration_str=duration_str,
    )


# ---------------------------------------------------------------------------
# Fahrt-Historie
# ---------------------------------------------------------------------------

@main_bp.route('/rides/history')
@login_required
@rider_required
def ride_history():
    rides = Ride.query.filter(
        Ride.rider_uid == current_user.uid,
        Ride.endzeit != None  # noqa: E711
    ).order_by(Ride.startzeit.desc()).all()
    return render_template('main/ride_history.html', rides=rides)


# ---------------------------------------------------------------------------
# Einzelne Fahrt / Quittung
# ---------------------------------------------------------------------------

@main_bp.route('/rides/<ride_uid>')
@login_required
@rider_required
def ride_detail(ride_uid):
    ride = Ride.query.get_or_404(ride_uid)
    if ride.rider_uid != current_user.uid:
        abort(403)
    transaction = Transaction.query.filter_by(ride_uid=ride.uid).first()
    return render_template(
        'main/ride_detail.html',
        ride=ride,
        scooter=ride.scooter,
        tariff=ride.tariff,
        transaction=transaction,
    )


# ---------------------------------------------------------------------------
# Zahlungsmethoden
# ---------------------------------------------------------------------------

@main_bp.route('/payment-methods', methods=['GET', 'POST'])
@login_required
@rider_required
def payment_methods():
    methods = PaymentMethod.query.filter_by(rider_uid=current_user.uid).all()
    form = PaymentMethodForm()
    if form.validate_on_submit():
        is_first = len(methods) == 0
        pm = PaymentMethod(
            rider_uid=current_user.uid,
            kartenidentifier_maskiert=form.kartenidentifier_maskiert.data,
            is_active=is_first,
        )
        db.session.add(pm)
        db.session.commit()
        flash('Zahlungsmethode hinzugefügt.', 'success')
        return redirect(url_for('main.payment_methods'))
    return render_template('main/payment_methods.html', methods=methods, form=form)


@main_bp.route('/payment-methods/<uid>/set-active', methods=['POST'])
@login_required
@rider_required
def payment_method_set_active(uid):
    pm = PaymentMethod.query.get_or_404(uid)
    if pm.rider_uid != current_user.uid:
        abort(403)
    for m in PaymentMethod.query.filter_by(rider_uid=current_user.uid).all():
        m.is_active = False
    pm.is_active = True
    db.session.commit()
    flash('Zahlungsmethode aktiviert.', 'success')
    return redirect(url_for('main.payment_methods'))


@main_bp.route('/payment-methods/<uid>/delete', methods=['POST'])
@login_required
@rider_required
def payment_method_delete(uid):
    pm = PaymentMethod.query.get_or_404(uid)
    if pm.rider_uid != current_user.uid:
        abort(403)
    all_methods = PaymentMethod.query.filter_by(rider_uid=current_user.uid).all()
    if pm.is_active and len(all_methods) == 1:
        flash('Letzte aktive Zahlungsmethode kann nicht gelöscht werden.', 'warning')
        return redirect(url_for('main.payment_methods'))
    was_active = pm.is_active
    db.session.delete(pm)
    db.session.commit()
    if was_active:
        next_pm = PaymentMethod.query.filter_by(rider_uid=current_user.uid).first()
        if next_pm:
            next_pm.is_active = True
            db.session.commit()
    flash('Zahlungsmethode entfernt.', 'success')
    return redirect(url_for('main.payment_methods'))
