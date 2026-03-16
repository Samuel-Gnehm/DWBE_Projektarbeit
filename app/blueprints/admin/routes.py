from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.extensions import db
from app.models.user import User
from app.models.scooter import Scooter
from app.models.tariff import Tariff
from app.models.ride import Ride
from app.models.transaction import Transaction
from app.models.vehicle_type import VehicleType
from app.utils import admin_required

from . import admin_bp
from .forms import TariffForm, VehicleTypeForm


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users     = User.query.filter_by(user_rolle='user').count()
    total_providers = User.query.filter_by(user_rolle='provider').count()
    total_scooters  = Scooter.query.count()
    active_scooters = Scooter.query.filter_by(status='available').count()
    rented_scooters = Scooter.query.filter_by(status='rented').count()
    total_rides     = Ride.query.filter(Ride.endzeit != None).count()  # noqa: E711
    active_rides    = Ride.query.filter_by(endzeit=None).count()
    total_revenue   = db.session.query(db.func.sum(Transaction.betrag)).filter_by(status='completed').scalar() or 0
    vehicle_types_list = VehicleType.query.order_by(VehicleType.name).all()
    active_tariffs = [(vt, Tariff.get_active(vt.uid)) for vt in vehicle_types_list]
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_providers=total_providers,
        total_scooters=total_scooters,
        active_scooters=active_scooters,
        rented_scooters=rented_scooters,
        total_rides=total_rides,
        active_rides=active_rides,
        total_revenue=total_revenue,
        active_tariffs=active_tariffs,
    )


# ---------------------------------------------------------------------------
# User-Verwaltung
# ---------------------------------------------------------------------------

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    rolle_filter = request.args.get('rolle')
    query = User.query
    if rolle_filter in ('user', 'provider', 'admin'):
        query = query.filter_by(user_rolle=rolle_filter)
    users_list = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list, rolle_filter=rolle_filter)


@admin_bp.route('/users/<uid>')
@login_required
@admin_required
def user_detail(uid):
    user = User.query.get_or_404(uid)
    rides = []
    scooters = []
    if user.user_rolle == 'user':
        rides = Ride.query.filter_by(rider_uid=user.uid).order_by(Ride.startzeit.desc()).limit(10).all()
    elif user.user_rolle == 'provider':
        scooters = Scooter.query.filter_by(uid_provider=user.uid).all()
    return render_template('admin/user_detail.html', user=user, rides=rides, scooters=scooters)


@admin_bp.route('/users/<uid>/toggle-status', methods=['POST'])
@login_required
@admin_required
def user_toggle_status(uid):
    user = User.query.get_or_404(uid)
    if user.user_rolle == 'admin':
        flash('Admin-Accounts können nicht deaktiviert werden.', 'warning')
        return redirect(url_for('admin.users'))
    user.status = 'deactivated' if user.status == 'active' else 'active'
    db.session.commit()
    aktion = 'deaktiviert' if user.status == 'deactivated' else 'aktiviert'
    flash(f'User {user.username} wurde {aktion}.', 'success')
    return redirect(url_for('admin.users'))


# ---------------------------------------------------------------------------
# Scooter-Verwaltung
# ---------------------------------------------------------------------------

@admin_bp.route('/scooters')
@login_required
@admin_required
def scooters():
    status_filter = request.args.get('status')
    query = Scooter.query
    if status_filter in ('available', 'rented', 'maintenance', 'disabled'):
        query = query.filter_by(status=status_filter)
    scooter_list = query.all()
    return render_template('admin/scooters.html', scooters=scooter_list, status_filter=status_filter)


@admin_bp.route('/scooters/<uid>/toggle-status', methods=['POST'])
@login_required
@admin_required
def scooter_toggle_status(uid):
    scooter = Scooter.query.get_or_404(uid)
    if scooter.status == 'rented':
        flash('Fahrzeug ist gerade verliehen.', 'warning')
        return redirect(url_for('admin.scooters'))
    if scooter.status == 'available':
        scooter.status = 'disabled'
    else:
        scooter.status = 'available'
    db.session.commit()
    flash(f'Fahrzeug-Status auf „{scooter.status}" gesetzt.', 'success')
    return redirect(url_for('admin.scooters'))


# ---------------------------------------------------------------------------
# Fahrten
# ---------------------------------------------------------------------------

@admin_bp.route('/rides')
@login_required
@admin_required
def rides():
    status_filter = request.args.get('status')
    query = Ride.query
    if status_filter == 'active':
        query = query.filter(Ride.endzeit == None)  # noqa: E711
    elif status_filter == 'completed':
        query = query.filter(Ride.endzeit != None)  # noqa: E711
    rides_list = query.order_by(Ride.startzeit.desc()).all()
    return render_template('admin/rides.html', rides=rides_list, status_filter=status_filter)


@admin_bp.route('/rides/<uid>')
@login_required
@admin_required
def ride_detail(uid):
    ride = Ride.query.get_or_404(uid)
    transaction = Transaction.query.filter_by(ride_uid=ride.uid).first()
    return render_template('admin/ride_detail.html', ride=ride, transaction=transaction)


# ---------------------------------------------------------------------------
# Transaktionen
# ---------------------------------------------------------------------------

@admin_bp.route('/transactions')
@login_required
@admin_required
def transactions():
    status_filter = request.args.get('status')
    query = Transaction.query
    if status_filter in ('pending', 'completed', 'failed'):
        query = query.filter_by(status=status_filter)
    transactions_list = query.order_by(Transaction.created_at.desc()).all()
    total_revenue = db.session.query(db.func.sum(Transaction.betrag)).filter_by(status='completed').scalar() or 0
    return render_template(
        'admin/transactions.html',
        transactions=transactions_list,
        total_revenue=total_revenue,
        status_filter=status_filter,
    )


# ---------------------------------------------------------------------------
# Fahrzeugtypen (nur Admin)
# ---------------------------------------------------------------------------

@admin_bp.route('/vehicle-types', methods=['GET', 'POST'])
@login_required
@admin_required
def vehicle_types():
    form = VehicleTypeForm()
    if form.validate_on_submit():
        existing = VehicleType.query.filter_by(name=form.name.data).first()
        if existing:
            flash(f'Fahrzeugtyp \u201e{form.name.data}\u201c existiert bereits.', 'warning')
        else:
            vt = VehicleType(name=form.name.data, description=form.description.data or None)
            db.session.add(vt)
            db.session.commit()
            flash(f'Fahrzeugtyp \u201e{vt.name}\u201c wurde angelegt.', 'success')
        return redirect(url_for('admin.vehicle_types'))
    all_types = VehicleType.query.order_by(VehicleType.name).all()
    return render_template('admin/vehicle_types.html', form=form, vehicle_types=all_types)


@admin_bp.route('/vehicle-types/<uid>/delete', methods=['POST'])
@login_required
@admin_required
def vehicle_type_delete(uid):
    vt = VehicleType.query.get_or_404(uid)
    if vt.scooters or vt.tariffs:
        flash(f'Fahrzeugtyp \u201e{vt.name}\u201c kann nicht gel\u00f6scht werden, da noch Fahrzeuge oder Tarife damit verkn\u00fcpft sind.', 'warning')
        return redirect(url_for('admin.vehicle_types'))
    db.session.delete(vt)
    db.session.commit()
    flash(f'Fahrzeugtyp \u201e{vt.name}\u201c gel\u00f6scht.', 'success')
    return redirect(url_for('admin.vehicle_types'))


# ---------------------------------------------------------------------------
# Tarife
# ---------------------------------------------------------------------------

def _vehicle_type_choices():
    types = VehicleType.query.order_by(VehicleType.name).all()
    return [(vt.uid, vt.name) for vt in types]


@admin_bp.route('/tariffs', methods=['GET', 'POST'])
@login_required
@admin_required
def tariffs():
    form = TariffForm()
    form.vehicle_type_uid.choices = _vehicle_type_choices()
    if form.validate_on_submit():
        active = Tariff.get_active(vehicle_type_uid=form.vehicle_type_uid.data)
        if active:
            active.is_active = False
            active.valid_to = form.valid_from.data
        new_tariff = Tariff(
            vehicle_type_uid=form.vehicle_type_uid.data,
            base_price=form.base_price.data,
            minute_price=form.minute_price.data,
            valid_from=form.valid_from.data,
            valid_to=None,
            is_active=True,
        )
        db.session.add(new_tariff)
        db.session.commit()
        flash('Neuer Tarif aktiviert.', 'success')
        return redirect(url_for('admin.tariffs'))
    all_tariffs = Tariff.query.order_by(Tariff.valid_from.desc()).all()
    vehicle_types_list = VehicleType.query.order_by(VehicleType.name).all()
    active_tariffs = {vt.uid: Tariff.get_active(vt.uid) for vt in vehicle_types_list}
    return render_template(
        'admin/tariffs.html',
        form=form,
        all_tariffs=all_tariffs,
        active_tariffs=active_tariffs,
        vehicle_types=vehicle_types_list,
    )
