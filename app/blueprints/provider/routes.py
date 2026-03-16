import uuid
from datetime import datetime

from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.scooter import Scooter
from app.models.tariff import Tariff
from app.models.vehicle_type import VehicleType
from app.utils import provider_required

from . import provider_bp
from .forms import ScooterForm


def _vehicle_type_choices():
    types = VehicleType.query.order_by(VehicleType.name).all()
    return [(vt.uid, vt.name) for vt in types]


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@provider_bp.route('/dashboard')
@login_required
@provider_required
def dashboard():
    scooter_count = Scooter.query.filter_by(uid_provider=current_user.uid).count()
    active_rides = Scooter.query.filter_by(
        uid_provider=current_user.uid, status='rented'
    ).count()
    vehicle_types_list = VehicleType.query.order_by(VehicleType.name).all()
    active_tariffs = [(vt, Tariff.get_active(vt.uid)) for vt in vehicle_types_list]
    low_battery_count = Scooter.query.filter(
        Scooter.uid_provider == current_user.uid,
        Scooter.battery_level < 25,
    ).count()
    return render_template(
        'provider/dashboard.html',
        scooter_count=scooter_count,
        active_rides=active_rides,
        active_tariffs=active_tariffs,
        low_battery_count=low_battery_count,
    )


# ---------------------------------------------------------------------------
# Scooter-Verwaltung
# ---------------------------------------------------------------------------

@provider_bp.route('/scooters')
@login_required
@provider_required
def scooters():
    scooter_list = Scooter.query.filter_by(uid_provider=current_user.uid).all()
    return render_template('provider/scooters.html', scooters=scooter_list)


@provider_bp.route('/scooters/add', methods=['GET', 'POST'])
@login_required
@provider_required
def scooter_add():
    form = ScooterForm()
    form.vehicle_type_uid.choices = _vehicle_type_choices()
    if form.validate_on_submit():
        new_status = form.status.data
        scooter = Scooter(
            uid_provider=current_user.uid,
            vehicle_type_uid=form.vehicle_type_uid.data,
            qr_code=str(uuid.uuid4()),
            model=form.model.data,
            battery_level=form.battery_level.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            status=new_status,
            gefahrene_km_gesamt=0.0,
            maintenance_since=datetime.utcnow() if new_status == 'maintenance' else None,
        )
        db.session.add(scooter)
        db.session.commit()
        flash('Fahrzeug erfolgreich hinzugefügt.', 'success')
        return redirect(url_for('provider.scooters'))
    return render_template('provider/scooter_form.html', form=form, title='Fahrzeug hinzufügen')


@provider_bp.route('/scooters/<uid>/edit', methods=['GET', 'POST'])
@login_required
@provider_required
def scooter_edit(uid):
    scooter = Scooter.query.get_or_404(uid)
    if scooter.uid_provider != current_user.uid:
        abort(403)
    form = ScooterForm(obj=scooter)
    form.vehicle_type_uid.choices = _vehicle_type_choices()
    if form.validate_on_submit():
        scooter.vehicle_type_uid = form.vehicle_type_uid.data
        scooter.model = form.model.data
        scooter.battery_level = form.battery_level.data
        scooter.latitude = form.latitude.data
        scooter.longitude = form.longitude.data
        if scooter.status != 'rented':
            new_status = form.status.data
            old_status = scooter.status
            # Leaving maintenance: apply accumulated charge (4% per minute, max 100)
            if old_status == 'maintenance' and new_status != 'maintenance':
                if scooter.maintenance_since:
                    minutes = (datetime.utcnow() - scooter.maintenance_since).total_seconds() / 60
                    scooter.battery_level = min(100, scooter.battery_level + int(minutes * 4))
                scooter.maintenance_since = None
            # Entering maintenance: record timestamp
            elif old_status != 'maintenance' and new_status == 'maintenance':
                scooter.maintenance_since = datetime.utcnow()
            scooter.status = new_status
        db.session.commit()
        flash('Fahrzeug erfolgreich aktualisiert.', 'success')
        return redirect(url_for('provider.scooters'))
    return render_template(
        'provider/scooter_form.html', form=form, title='Fahrzeug bearbeiten', scooter=scooter
    )


@provider_bp.route('/scooters/<uid>/delete', methods=['POST'])
@login_required
@provider_required
def scooter_delete(uid):
    scooter = Scooter.query.get_or_404(uid)
    if scooter.uid_provider != current_user.uid:
        abort(403)
    if scooter.status == 'rented':
        flash('Fahrzeug ist gerade verliehen und kann nicht deaktiviert werden.', 'warning')
        return redirect(url_for('provider.scooters'))
    scooter.status = 'disabled'
    db.session.commit()
    flash('Fahrzeug deaktiviert.', 'success')
    return redirect(url_for('provider.scooters'))


# ---------------------------------------------------------------------------
# Tarife
# ---------------------------------------------------------------------------

@provider_bp.route('/tariffs')
@login_required
@provider_required
def tariffs():
    vehicle_types_list = VehicleType.query.order_by(VehicleType.name).all()
    active_tariffs = [(vt, Tariff.get_active(vt.uid)) for vt in vehicle_types_list]
    all_tariffs = Tariff.query.order_by(Tariff.valid_from.desc()).all()
    return render_template(
        'provider/tariffs.html',
        active_tariffs=active_tariffs,
        all_tariffs=all_tariffs,
    )


