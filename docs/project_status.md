# Projektstatus – E-Scooter Verleih (DWBE_Projektarbeit)

Stand: 2026-03-16 | Phasen 1–5a abgeschlossen

---

## 1. Implementierte Routen

### Blueprint `main` – Prefix `/`

| Methode      | URL                                    | Funktion                  | Beschreibung                                  |
|--------------|----------------------------------------|---------------------------|-----------------------------------------------|
| GET          | `/`                                    | `index`                   | Redirect auf Dashboard je nach Rolle          |
| GET, POST    | `/dashboard`                           | `dashboard`               | Rider-Dashboard: aktive Fahrt + Statistiken   |
| GET, POST    | `/scooters`                            | `scooters`                | Verfügbare Scooter auflisten                  |
| POST         | `/rides/start/<scooter_uid>`           | `ride_start`              | Neue Fahrt starten                            |
| GET, POST    | `/rides/active`                        | `ride_active`             | Aktive Fahrt anzeigen mit Preis-Vorschau      |
| GET, POST    | `/rides/end/<ride_uid>`               | `ride_end`                | Fahrt beenden und Preis berechnen             |
| GET          | `/rides/history`                       | `ride_history`            | Abgeschlossene Fahrten anzeigen               |
| GET          | `/rides/<ride_uid>`                   | `ride_detail`             | Quittung / Fahrtdetails                       |
| GET, POST    | `/payment-methods`                     | `payment_methods`         | Zahlungsmethoden verwalten                    |
| POST         | `/payment-methods/<uid>/set-active`    | `payment_method_set_active` | Zahlungsmethode als aktiv setzen            |
| POST         | `/payment-methods/<uid>/delete`        | `payment_method_delete`   | Zahlungsmethode löschen                       |

### Blueprint `auth` – Prefix `/auth`

| Methode      | URL               | Funktion   | Beschreibung                               |
|--------------|-------------------|------------|--------------------------------------------|
| GET, POST    | `/auth/register`  | `register` | Registrierung (Rolle: user oder provider)  |
| GET, POST    | `/auth/login`     | `login`    | Login mit rollenbasiertem Redirect         |
| GET          | `/auth/logout`    | `logout`   | Logout                                     |

### Blueprint `provider` – Prefix `/provider`

| Methode      | URL                                    | Funktion          | Beschreibung                            |
|--------------|----------------------------------------|-------------------|-----------------------------------------|
| GET          | `/provider/dashboard`                  | `dashboard`       | Provider-Dashboard mit Scooter-Statistik |
| GET          | `/provider/scooters`                   | `scooters`        | Scooter des Providers auflisten          |
| GET, POST    | `/provider/scooters/add`               | `scooter_add`     | Neuen Scooter anlegen                   |
| GET, POST    | `/provider/scooters/<uid>/edit`        | `scooter_edit`    | Scooter bearbeiten (eigene only)        |
| POST         | `/provider/scooters/<uid>/delete`      | `scooter_delete`  | Scooter deaktivieren                    |
| GET          | `/provider/tariffs`                    | `tariffs`         | Tarife einsehen                         |

### Blueprint `admin` – Prefix `/admin`

| Methode      | URL                                    | Funktion                  | Beschreibung                                  |
|--------------|----------------------------------------|---------------------------|-----------------------------------------------|
| GET          | `/admin/dashboard`                     | `dashboard`               | Admin-Dashboard mit Systemstatistik           |
| GET          | `/admin/users`                         | `users`                   | Alle User (filterbar nach Rolle)              |
| GET          | `/admin/users/<uid>`                   | `user_detail`             | Userdetails und Relationen                    |
| POST         | `/admin/users/<uid>/toggle-status`     | `user_toggle_status`      | User aktivieren / deaktivieren                |
| GET          | `/admin/scooters`                      | `scooters`                | Alle Scooter (filterbar nach Status)          |
| POST         | `/admin/scooters/<uid>/toggle-status`  | `scooter_toggle_status`   | Scooter-Verfügbarkeit umschalten              |
| GET          | `/admin/rides`                         | `rides`                   | Alle Fahrten (filterbar nach Status)          |
| GET          | `/admin/rides/<uid>`                   | `ride_detail`             | Fahrt- und Transaktionsdetails                |
| GET          | `/admin/transactions`                  | `transactions`            | Alle Transaktionen (filterbar nach Status)    |
| GET, POST    | `/admin/vehicle-types`                 | `vehicle_types`           | Fahrzeugtypen anlegen / auflisten             |
| GET, POST    | `/admin/vehicle-types/<uid>/edit`      | `vehicle_type_edit`       | Fahrzeugtyp bearbeiten                        |
| POST         | `/admin/vehicle-types/<uid>/delete`    | `vehicle_type_delete`     | Fahrzeugtyp löschen                           |
| GET, POST    | `/admin/tariffs`                       | `tariffs`                 | Tarife anlegen / verwalten                    |

---

## 2. API-Endpunkte

Blueprint `api` – Prefix `/api` | Auth via JWT Bearer Token

| Methode | URL                    | Auth erforderlich       | Beschreibung                          |
|---------|------------------------|-------------------------|---------------------------------------|
| POST    | `/api/auth/login`      | Nein                    | Login – gibt JWT-Token zurück         |
| GET     | `/api/scooters`        | Nein (public)           | Alle verfügbaren Scooter (JSON)       |
| GET     | `/api/scooters/<uid>`  | Nein (public)           | Einzelner Scooter (JSON)              |
| POST    | `/api/scooters`        | Ja – Rolle `provider`   | Neuen Scooter anlegen                 |
| GET     | `/api/rides`           | Ja – Rolle `user`       | Eigene abgeschlossene Fahrten         |
| GET     | `/api/rides/<uid>`     | Ja – Rolle `user`       | Einzelne Fahrt (nur eigene)           |
| GET     | `/api/tariffs/active`  | Nein (public)           | Aktiver Tarif                         |
| GET     | `/api/transactions`    | Ja – Rolle `user`       | Eigene Transaktionen                  |

---

## 3. Datenbankmodelle

### `User` → Tabelle `users`

| Feld              | Typ              |
|-------------------|------------------|
| `uid`             | String(36) PK    |
| `vorname`         | String(100)      |
| `nachname`        | String(100)      |
| `username`        | String(50) UNIQUE|
| `email`           | String(255) UNIQUE|
| `passwort_hash`   | String(255)      |
| `user_rolle`      | String(20)       |
| `status`          | String(20)       |
| `last_login`      | DateTime         |
| `created_at`      | DateTime         |

### `VehicleType` → Tabelle `vehicle_types`

| Feld                        | Typ              |
|-----------------------------|------------------|
| `uid`                       | String(36) PK    |
| `name`                      | String(100) UNIQUE|
| `description`               | String(255)      |
| `meter_per_minute`          | Integer          |
| `battery_drain_per_minute`  | Numeric(5,2)     |
| `battery_charge_per_minute` | Numeric(5,2)     |

### `Scooter` → Tabelle `scooters`

| Feld                    | Typ              |
|-------------------------|------------------|
| `uid`                   | String(36) PK    |
| `uid_provider`          | String(36) FK    |
| `vehicle_type_uid`      | String(36) FK    |
| `model`                 | String(100)      |
| `qr_code`               | String(100) UNIQUE|
| `status`                | String(20)       |
| `gefahrene_km_gesamt`   | Numeric(10,2)    |
| `battery_level`         | SmallInteger     |
| `maintenance_since`     | DateTime         |
| `latitude`              | Numeric(9,6)     |
| `longitude`             | Numeric(9,6)     |
| `created_at`            | DateTime         |

### `Tariff` → Tabelle `tariffs`

| Feld               | Typ              |
|--------------------|------------------|
| `uid`              | String(36) PK    |
| `vehicle_type_uid` | String(36) FK    |
| `base_price`       | Numeric(10,2)    |
| `minute_price`     | Numeric(10,2)    |
| `valid_from`       | Date             |
| `valid_to`         | Date             |
| `is_active`        | Boolean          |

### `Ride` → Tabelle `rides`

| Feld            | Typ              |
|-----------------|------------------|
| `uid`           | String(36) PK    |
| `rider_uid`     | String(36) FK    |
| `scooter_uid`   | String(36) FK    |
| `tarif_uid`     | String(36) FK    |
| `startzeit`     | DateTime         |
| `endzeit`       | DateTime         |
| `gesamtpreis`   | Numeric(10,2)    |
| `gefahrene_km`  | Numeric(10,2)    |
| `created_at`    | DateTime         |

### `PaymentMethod` → Tabelle `payment_methods`

| Feld                          | Typ              |
|-------------------------------|------------------|
| `uid`                         | String(36) PK    |
| `rider_uid`                   | String(36) FK    |
| `kartenidentifier_maskiert`   | String(25)       |
| `is_active`                   | Boolean          |
| `created_at`                  | DateTime         |

### `Transaction` → Tabelle `transactions`

| Feld                  | Typ              |
|-----------------------|------------------|
| `uid`                 | String(36) PK    |
| `ride_uid`            | String(36) FK    |
| `payment_method_uid`  | String(36) FK    |
| `betrag`              | Numeric(10,2)    |
| `status`              | String(20)       |
| `created_at`          | DateTime         |

---

## 4. Flask-Extensions

| Extension          | Paket               | Zweck                                               |
|--------------------|---------------------|-----------------------------------------------------|
| `SQLAlchemy`       | flask-sqlalchemy    | ORM – Datenbankzugriff und Modellmapping            |
| `Migrate`          | flask-migrate       | Datenbankmigrationen via Alembic                    |
| `LoginManager`     | flask-login         | Session-basierte User-Authentifizierung (Web-UI)    |
| `CSRFProtect`      | flask-wtf           | CSRF-Schutz für HTML-Formulare                      |
| `JWTManager`       | flask-jwt-extended  | JWT-Authentifizierung für die REST-API              |

---

## 5. Projektstruktur

```
DWBE_Projektarbeit/
├── run.py                        # Einstiegspunkt (development)
├── seed.py                       # Datenbank-Seed-Skript
├── requirements.txt
├── .env / .env.example
├── .gitignore
│
├── app/
│   ├── __init__.py               # App-Factory (create_app)
│   ├── config.py                 # DevelopmentConfig, ProductionConfig, TestingConfig
│   ├── extensions.py             # db, login_manager, migrate, csrf, jwt
│   ├── utils.py                  # Rollen-Dekoratoren (role_required)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── scooter.py
│   │   ├── tariff.py
│   │   ├── ride.py
│   │   ├── payment_method.py
│   │   ├── transaction.py
│   │   └── vehicle_type.py       # Zusätzlich gegenüber Phase-1-Spezifikation
│   │
│   ├── blueprints/
│   │   ├── main/                 # Rider-UI
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── forms.py
│   │   ├── provider/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   └── api/
│   │       ├── __init__.py
│   │       └── routes.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── macros.html
│   │   ├── auth/         (login.html, register.html)
│   │   ├── main/         (dashboard, scooters, rides, payment_methods)
│   │   ├── provider/     (dashboard, scooters, tariffs)
│   │   ├── admin/        (dashboard, users, scooters, rides, transactions, tariffs, vehicle_types)
│   │   └── errors/       (403.html, 404.html)
│   │
│   └── static/
│       └── css/theme.css
│
├── migrations/                   # Flask-Migrate / Alembic
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py              # T01–T03
│   ├── test_access.py            # T04–T05
│   ├── test_provider.py          # T06–T07
│   ├── test_rider.py             # T08–T10
│   └── test_api.py               # T11–T12
│
├── docs/
│   ├── requirements_phase1
│   ├── requirements_phase2
│   ├── requirements_phase3a_provider
│   ├── requirements_phase3b_user
│   ├── requirements_phase3c_admin
│   ├── requirements_phase4
│   ├── requirements_phase5a_testing
│   ├── SQL_DataModel.md
│   └── project_status.md         # diese Datei
│
└── SQL/
    └── SQL_Schema.sql
```

---

## 6. Besonderheiten und Abweichungen vom Requirements-File

### Ergänzungen gegenüber der Spezifikation

| Bereich | Abweichung |
|---------|------------|
| **Modell `VehicleType`** | In Phase 1 nicht vorgesehen – in Phase 5 (Commit `6937884`) nachträglich als eigenes Modell eingeführt. Ermöglicht typenspezifische Tarife und Simulationsparameter (`meter_per_minute`, `battery_drain_per_minute`, `battery_charge_per_minute`). |
| **`Tariff.vehicle_type_uid`** | FK auf `vehicle_types` hinzugefügt – ursprüngliche Spezifikation sah keinen Bezug zwischen Tarif und Fahrzeugtyp vor. |
| **`Scooter.vehicle_type_uid`** | Zusätzlicher FK auf `vehicle_types` – ermöglicht typenspezifische Fahrzeugverwaltung. |
| **`Scooter.maintenance_since`** | Zusätzliches Feld für Wartungs-Tracking, nicht in Phase-1-Spezifikation enthalten. |
| **`CSRFProtect`** | In Phase 1 nur `db`, `login_manager`, `migrate` gefordert. `CSRFProtect` (flask-wtf) wurde zusätzlich in `extensions.py` initialisiert. |
| **Blueprint `provider`** | Phase 1 sah nur `main`, `auth`, `api` vor. `provider` und `admin` wurden in Phase 2–3 ergänzt. |
| **`app/utils.py`** | Rollen-Dekoratoren (`role_required`) – nicht in der Spezifikation vorgesehen, aber für sauberes RBAC sinnvoll. |
| **`macros.html`** | Template-Makros für wiederverwendbare UI-Komponenten – nicht spezifiziert, aber implementiert. |
| **`seed.py`** | Seed-Skript für Testdaten – nicht in Requirements enthalten. |
| **`TestingConfig`** | In Phase 5a gefordert – ist implementiert, inkl. SQLite In-Memory und CSRF-Deaktivierung. |

### Nicht implementierte Requirements

| Bereich | Stand |
|---------|-------|
| Deployment (Phase 5b) | Noch nicht begonnen – Linux-VM-Deployment ausstehend. |
| `test_access.py` – `conftest.py` fehlt `login` Import | `conftest.py` ist vorhanden und enthält die `login`-Hilfsfunktion. Tests sollten funktionieren. |

### Authentifizierungsarchitektur

Die App verwendet zwei parallele Auth-Systeme – dies entspricht der Spezifikation:

- **Flask-Login** (Session-Cookies) für die Web-UI
- **Flask-JWT-Extended** (Bearer Token) für die REST-API unter `/api/`

CSRF-Schutz gilt nur für die Web-UI; die API ist davon ausgenommen (kein Cookie, kein Browser-Formular).
