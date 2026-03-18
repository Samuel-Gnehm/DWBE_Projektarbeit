# Website-Beschreibung – E-Scooter Verleih (DWBE_Projektarbeit)

Stand: 2026-03-16 | Vollständige Beschreibung aller Ansichten, Elemente und Funktionen

---

## Inhaltsverzeichnis

1. [Allgemeine Struktur & Navigation](#1-allgemeine-struktur--navigation)
2. [Authentifizierung (alle Rollen)](#2-authentifizierung-alle-rollen)
3. [Rolle: Fahrer (user)](#3-rolle-fahrer-user)
4. [Rolle: Anbieter (provider)](#4-rolle-anbieter-provider)
5. [Rolle: Administrator (admin)](#5-rolle-administrator-admin)
6. [REST-API (technisch)](#6-rest-api-technisch)
7. [Fehlerseiten](#7-fehlerseiten)

---

## 1. Allgemeine Struktur & Navigation

### Layout (`base.html`)

Das gesamte Frontend basiert auf einem einheitlichen Layout mit **Bootstrap 5.3** und einem angepassten CSS-Theme (`static/css/theme.css`).

**Seitenaufbau:**
- **Linke Sidebar** (Desktop) / **Hamburger-Menü** (Mobile): Navigationsleiste mit rollenspezifischen Links
- **Hauptbereich (Content-Area)**: Zeigt den Inhalt der jeweiligen Route
- **Footer**: Statischer Seitenfuss
- **Flash-Message-Bereich**: Direkt unterhalb der Navigation – zeigt Erfolgs- (grün), Fehler- (rot) und Info-Meldungen (blau) nach Formular-Aktionen

**Sidebar-Inhalte nach Rolle:**

| Rolle | Sichtbare Links |
|-------|----------------|
| **user** | Dashboard, Scooter, Aktive Fahrt\*, Fahrthistorie, Zahlungsmethoden |
| **provider** | Dashboard, Meine Scooter, Tarife |
| **admin** | Dashboard, Benutzer, Scooter, Fahrten, Transaktionen, Fahrzeugtypen, Tarife |

\* Der Link "Aktive Fahrt" erscheint in der Sidebar **nur wenn eine aktive Fahrt vorhanden ist** (wird bei jedem Request via `context_processor` injiziert).

**Flash-Messages:** Werden nach jeder Aktion (Login, Formular-Submit, Fehler) als Banner angezeigt und verschwinden beim nächsten Seitenaufruf.

---

## 2. Authentifizierung (alle Rollen)

### 2.1 Registrierung – `/auth/register` (GET/POST)

**Zweck:** Neues Benutzerkonto erstellen (Fahrer oder Anbieter)

**Seitenelemente:**
- Überschrift: "Registrieren"
- Formular mit folgenden Feldern:

| Feld | Typ | Pflicht | Validierung |
|------|-----|---------|-------------|
| Vorname | Textfeld | Ja | Max. 100 Zeichen |
| Nachname | Textfeld | Ja | Max. 100 Zeichen |
| Benutzername | Textfeld | Ja | Max. 50 Zeichen, muss eindeutig sein |
| E-Mail | E-Mail-Feld | Ja | Gültige E-Mail-Adresse, muss eindeutig sein |
| Passwort | Passwortfeld | Ja | Mindestens 8 Zeichen |
| Passwort bestätigen | Passwortfeld | Ja | Muss mit Passwort übereinstimmen |
| Rolle | Dropdown | Ja | "Fahrer" (user) oder "Anbieter" (provider) |
| Registrieren | Submit-Button | – | – |

- Link: "Bereits registriert? Hier anmelden" → `/auth/login`

**Backend-Logik (POST):**
1. Formular wird validiert (CSRF-Token, Pflichtfelder, Passwort-Übereinstimmung)
2. Prüfung: Username bereits vergeben → Flash-Fehler
3. Prüfung: E-Mail bereits vergeben → Flash-Fehler
4. Passwort wird mit `werkzeug.security.generate_password_hash` gehasht
5. Neues `User`-Objekt wird erstellt mit:
   - `uid` = zufällige UUID
   - `vorname`, `nachname`, `username`, `email` aus Formular
   - `passwort_hash` = gehashtes Passwort
   - `user_rolle` = "user" oder "provider"
   - `status` = "active"
   - `created_at` = aktueller Zeitstempel
6. Wird in Tabelle `users` gespeichert (`db.session.add` + `db.session.commit`)
7. Flash-Meldung: "Konto erfolgreich erstellt."
8. **Redirect:** → `/auth/login`

---

### 2.2 Login – `/auth/login` (GET/POST)

**Zweck:** Anmeldung an der Web-Applikation

**Seitenelemente:**
- Überschrift: "Anmelden"
- Formular:

| Feld | Typ | Pflicht |
|------|-----|---------|
| Benutzername | Textfeld | Ja |
| Passwort | Passwortfeld | Ja |
| Angemeldet bleiben | Checkbox | Nein |
| Anmelden | Submit-Button | – |

- Link: "Noch kein Konto? Hier registrieren" → `/auth/register`

**Backend-Logik (POST):**
1. Username aus DB gesucht → nicht gefunden: Flash-Fehler "Ungültige Zugangsdaten"
2. Passwort-Hash-Vergleich → falsch: Flash-Fehler "Ungültige Zugangsdaten"
3. `user.status == 'deactivated'` → Flash-Fehler "Konto deaktiviert"
4. `login_user(user, remember=remember)` → Session wird erstellt (Flask-Login)
5. `user.last_login` wird auf aktuellen Zeitstempel gesetzt und gespeichert
6. **Redirect je nach Rolle:**
   - `admin` → `/admin/dashboard`
   - `provider` → `/provider/dashboard`
   - `user` → `/dashboard`

---

### 2.3 Logout – `/auth/logout` (GET)

**Zweck:** Session beenden

**Backend-Logik:**
1. `logout_user()` → Flask-Login Session wird gelöscht
2. **Redirect:** → `/auth/login`

---

## 3. Rolle: Fahrer (user)

### 3.1 Startseite / Index – `/` (GET)

**Zweck:** Intelligenter Redirect nach Login

**Backend-Logik:**
- Nicht eingeloggt → `/auth/login`
- Rolle `admin` → `/admin/dashboard`
- Rolle `provider` → `/provider/dashboard`
- Rolle `user` → `/dashboard`

---

### 3.2 Dashboard – `/dashboard` (GET)

**Zweck:** Übersichtsseite für den Fahrer

**Seitenelemente:**

**Statistik-Karten (oben):**

| Karte | Inhalt | Quelle |
|-------|--------|--------|
| Verfügbare Scooter | Anzahl Scooter mit Status "available" | Tabelle `scooters` |
| Abgeschlossene Fahrten | Anzahl eigener beendeter Fahrten | Tabelle `rides` (rider_uid = current_user) |
| Zahlungsmethode | "Aktiv" oder "Keine aktive Methode" | Tabelle `payment_methods` (is_active=True) |

**Aktive Fahrt-Banner** (nur wenn aktive Fahrt vorhanden):
- Anzeige: "Du hast eine aktive Fahrt!" mit Button "Zur aktiven Fahrt" → `/rides/active`

**Quick-Action-Buttons:**
- "Scooter mieten" → `/scooters`
- "Fahrthistorie" → `/rides/history`
- "Zahlungsmethoden" → `/payment-methods`

**Backend-Logik:**
- `active_ride = Ride.get_active_for(current_user.uid)` – sucht in `rides` nach `endzeit IS NULL` für diesen User
- Statistiken werden direkt aus DB abgefragt

---

### 3.3 Scooter-Liste – `/scooters` (GET)

**Zweck:** Verfügbare Scooter anzeigen und Fahrt starten

**Seitenelemente:**

**Filter/Hinweis-Bereich:**
- Info-Banner wenn keine aktive Zahlungsmethode vorhanden (kann nicht mieten)
- Info-Banner wenn bereits eine aktive Fahrt läuft (kann keinen neuen Scooter mieten)

**Scooter-Grid (Karten):**

Für jeden verfügbaren Scooter (Status = "available") wird eine Karte angezeigt mit:

| Element | Inhalt |
|---------|--------|
| Scooter-Name | `model` des Scooters |
| Fahrzeugtyp | `VehicleType.name` |
| Batterie | `battery_level`% mit visuellem Balken (grün/gelb/rot je nach %) |
| Standort | `latitude` / `longitude` als Koordinaten |
| QR-Code | `qr_code` des Scooters |
| Tarif | Grundpreis + Minutenpreis aus aktivem Tarif für diesen Fahrzeugtyp |
| Button "Fahrt starten" | POST `/rides/start/<scooter_uid>` |

**Button-Verhalten:**
- Button ist **deaktiviert** wenn: keine Zahlungsmethode aktiv ODER bereits eine Fahrt läuft
- Button ist **aktiv** wenn: Zahlungsmethode vorhanden + kein aktiver Ride

**Backend-Logik (GET):**
- Lädt alle Scooter mit `status='available'`
- Prüft `PaymentMethod.get_active_for(current_user.uid)`
- Prüft `Ride.get_active_for(current_user.uid)`

---

### 3.4 Fahrt starten – `/rides/start/<scooter_uid>` (POST)

**Zweck:** Neue Fahrt beginnen (kein eigenes Template – nur Logik + Redirect)

**Backend-Logik:**
1. Scooter mit `uid = scooter_uid` wird geladen → nicht gefunden: 404
2. Scooter-Status muss "available" sein → sonst Flash-Fehler + Redirect `/scooters`
3. Keine aktive Fahrt für User vorhanden → sonst Flash-Fehler + Redirect `/rides/active`
4. Aktive Zahlungsmethode muss vorhanden sein → sonst Flash-Fehler + Redirect `/payment-methods`
5. Aktiver Tarif für den Fahrzeugtyp des Scooters muss vorhanden sein → sonst Flash-Fehler
6. Neues `Ride`-Objekt erstellt:
   - `uid` = neue UUID
   - `rider_uid` = `current_user.uid`
   - `scooter_uid` = `scooter_uid`
   - `tarif_uid` = aktiver Tarif UID
   - `startzeit` = `datetime.utcnow()`
   - `endzeit` = NULL (Fahrt noch aktiv)
   - `gesamtpreis` = NULL
   - `gefahrene_km` = NULL
7. Scooter-Status wird auf "rented" gesetzt
8. Gespeichert in `rides` und `scooters`
9. Flash-Meldung: "Fahrt gestartet!"
10. **Redirect:** → `/rides/active`

---

### 3.5 Aktive Fahrt – `/rides/active` (GET)

**Zweck:** Laufende Fahrt anzeigen mit Echtzeit-Kostenvorschau

**Seitenelemente:**

| Element | Inhalt |
|---------|--------|
| Scooter-Modell | `scooter.model` |
| Fahrzeugtyp | `scooter.vehicle_type.name` |
| Startzeit | `ride.startzeit` formatiert |
| Bisherige Dauer | `ride.duration_str` (HH:MM:SS, berechnet aus startzeit bis jetzt) |
| Aktueller Preis | `ride.calculate_price()` – Grundpreis + (Minuten × Minutenpreis) |
| Aktiver Tarif | Grundpreis und Minutenpreis angezeigt |
| Button "Fahrt beenden" | Link → `/rides/end/<ride_uid>` |

**Preis-Berechnung (`calculate_price()`):**
```
elapsed_minutes = (datetime.utcnow() - ride.startzeit).total_seconds() / 60
preis = tarif.base_price + (elapsed_minutes × tarif.minute_price)
```

**Backend-Logik:**
- `Ride.get_active_for(current_user.uid)` → keine Fahrt gefunden: Redirect `/dashboard`

---

### 3.6 Fahrt beenden – `/rides/end/<ride_uid>` (GET/POST)

**Zweck:** Fahrt abschliessen, Endort wählen, Preis festschreiben

**Seitenelemente (GET):**

| Element | Inhalt |
|---------|--------|
| **Leaflet-Karte** | Interaktive Karte, Startposition = aktuelle Scooter-Koordinaten |
| Marker setzen | User klickt auf Karte → setzt Drop-off-Marker |
| Latitude-Feld (versteckt) | Wird automatisch aus Marker-Position befüllt |
| Longitude-Feld (versteckt) | Wird automatisch aus Marker-Position befüllt |
| Kosten-Vorschau | Zeigt berechneten Preis bis zum Zeitpunkt des GET-Requests |
| Button "Fahrt beenden" | Sendet Formular ab (POST) |

**Backend-Logik (POST):**
1. Ride geladen, muss `rider_uid = current_user.uid` sein → sonst 403
2. `endzeit = datetime.utcnow()` gesetzt
3. `gefahrene_km` berechnet:
   ```
   duration_minutes = (endzeit - startzeit).total_seconds() / 60
   gefahrene_km = (vehicle_type.meter_per_minute × duration_minutes) / 1000
   ```
4. `gesamtpreis = ride.calculate_price()` (zum Zeitpunkt des POSTs berechnet)
5. Scooter-Koordinaten aktualisiert (latitude/longitude aus Formular)
6. Scooter-Batterie reduziert:
   ```
   battery_drain = vehicle_type.battery_drain_per_minute × duration_minutes
   scooter.battery_level = max(0, battery_level - battery_drain)
   ```
7. Scooter-Status zurück auf "available"
8. `scooter.gefahrene_km_gesamt` += gefahrene_km
9. **Transaction erstellt:**
   - `uid` = neue UUID
   - `ride_uid` = ride.uid
   - `payment_method_uid` = aktive Zahlungsmethode des Users
   - `betrag` = gesamtpreis
   - `status` = "completed"
10. Alle Änderungen gespeichert (`rides`, `scooters`, `transactions`)
11. **Redirect:** → `/rides/<ride_uid>` (Quittungsseite)

---

### 3.7 Fahrtdetail / Quittung – `/rides/<ride_uid>` (GET)

**Zweck:** Quittung und Fahrtdetails nach Abschluss

**Seitenelemente:**

| Element | Inhalt |
|---------|--------|
| Scooter-Modell | `scooter.model` |
| Fahrzeugtyp | `scooter.vehicle_type.name` |
| Startzeit | `ride.startzeit` formatiert |
| Endzeit | `ride.endzeit` formatiert |
| Dauer | `ride.duration_str` |
| Gefahrene KM | `ride.gefahrene_km` |
| Grundpreis | `tarif.base_price` |
| Minutenpreis | `tarif.minute_price` |
| **Gesamtpreis** | `ride.gesamtpreis` (fettgedruckt) |
| Zahlungsmethode | Maskierte Kartennummer der verwendeten Zahlungsmethode |
| Transaktions-Status | `transaction.status` mit Farbkodierung |
| Button "Zurück zur Übersicht" | → `/rides/history` |

**Backend-Logik:**
- Ride wird geladen, `rider_uid` muss `current_user.uid` entsprechen → sonst 403
- Zugehörige Transaction via `transaction.ride_uid` geladen

---

### 3.8 Fahrthistorie – `/rides/history` (GET)

**Zweck:** Alle abgeschlossenen Fahrten des Fahrers

**Seitenelemente:**

**Tabelle mit Spalten:**

| Spalte | Inhalt |
|--------|--------|
| Datum | `ride.startzeit` |
| Scooter | `scooter.model` |
| Dauer | `ride.duration_str` |
| KM | `ride.gefahrene_km` |
| Preis | `ride.gesamtpreis` CHF |
| Detail | Link "Details" → `/rides/<ride_uid>` |

**Wenn keine Fahrten vorhanden:**
- Info-Meldung: "Noch keine Fahrten vorhanden" mit Button "Scooter mieten" → `/scooters`

**Backend-Logik:**
- Lädt alle `Ride`-Einträge mit `rider_uid = current_user.uid` und `endzeit IS NOT NULL`
- Sortiert nach `startzeit DESC` (neueste zuerst)

---

### 3.9 Zahlungsmethoden – `/payment-methods` (GET/POST)

**Zweck:** Zahlungsmethoden verwalten (hinzufügen, aktivieren, löschen)

**Seitenelemente (GET):**

**Liste bestehender Zahlungsmethoden:**

| Element | Inhalt |
|---------|--------|
| Kartennummer (maskiert) | `kartenidentifier_maskiert` (z.B. `**** **** **** 1234`) |
| Status-Badge | "Aktiv" (grün) oder "Inaktiv" (grau) |
| Button "Als aktiv setzen" | POST `/payment-methods/<uid>/set-active` (nur bei inaktiven) |
| Button "Löschen" | POST `/payment-methods/<uid>/delete` |

**Formular "Neue Zahlungsmethode hinzufügen":**

| Feld | Typ | Pflicht | Validierung |
|------|-----|---------|-------------|
| Kartenidentifier (maskiert) | Textfeld | Ja | 4–25 Zeichen |
| Hinzufügen | Submit-Button | – | – |

**Backend-Logik (POST – Neue Methode):**
1. Formular validieren
2. Neues `PaymentMethod`-Objekt:
   - `uid` = neue UUID
   - `rider_uid` = `current_user.uid`
   - `kartenidentifier_maskiert` = Wert aus Formular
   - `is_active` = False (standardmässig inaktiv)
   - `created_at` = aktueller Zeitstempel
3. Gespeichert in Tabelle `payment_methods`
4. Flash: "Zahlungsmethode hinzugefügt."
5. **Redirect:** → `/payment-methods`

---

### 3.10 Zahlungsmethode aktivieren – `/payment-methods/<uid>/set-active` (POST)

**Backend-Logik:**
1. Alle bestehenden Zahlungsmethoden des Users: `is_active = False`
2. Gewählte Methode: `is_active = True`
3. Gespeichert in `payment_methods`
4. Flash: "Zahlungsmethode aktiviert."
5. **Redirect:** → `/payment-methods`

---

### 3.11 Zahlungsmethode löschen – `/payment-methods/<uid>/delete` (POST)

**Backend-Logik:**
1. Methode muss `rider_uid = current_user.uid` haben → sonst 403
2. Prüfung: Methode darf nicht die einzige aktive sein, wenn eine Fahrt aktiv ist
3. `db.session.delete(payment_method)`
4. Gespeichert
5. Flash: "Zahlungsmethode gelöscht."
6. **Redirect:** → `/payment-methods`

---

## 4. Rolle: Anbieter (provider)

### 4.1 Provider-Dashboard – `/provider/dashboard` (GET)

**Zweck:** Übersicht über die eigene Scooter-Flotte

**Seitenelemente:**

**Statistik-Karten:**

| Karte | Inhalt | Quelle |
|-------|--------|--------|
| Meine Scooter | Anzahl eigener Scooter (nicht "disabled") | `scooters` WHERE `uid_provider = current_user.uid` |
| Aktive Vermietungen | Anzahl aktuell vermieteter eigener Scooter (Status "rented") | `scooters` + `rides` |
| Niedriger Akkustand | Anzahl Scooter mit `battery_level < 20%` | `scooters` |

**Quick-Links:**
- "Meine Scooter verwalten" → `/provider/scooters`
- "Neuen Scooter hinzufügen" → `/provider/scooters/add`
- "Tarife ansehen" → `/provider/tariffs`

**Warnbereich (wenn Scooter mit niedrigem Akku vorhanden):**
- Liste der Scooter mit Akku < 20% mit Modellname und aktuellem Ladestand

---

### 4.2 Scooter-Liste – `/provider/scooters` (GET)

**Zweck:** Eigene Scooter verwalten und auf Karte visualisieren

**Seitenelemente:**

**Leaflet-Karte (oben):**
- Zeigt alle eigenen Scooter als Marker auf einer interaktiven Karte
- Marker-Farbe je nach Status (grün = available, grau = rented, orange = maintenance, rot = disabled)
- Klick auf Marker: Popup mit Scooter-Modell, Batterie und Link "Bearbeiten"

**Tabelle (unten):**

| Spalte | Inhalt |
|--------|--------|
| Modell | `scooter.model` |
| Fahrzeugtyp | `vehicle_type.name` |
| Status | Farbiges Badge (available/rented/maintenance/disabled) |
| Batterie | `battery_level`% |
| Standort | Koordinaten `lat, lon` |
| QR-Code | `qr_code` |
| Aktionen | Buttons "Bearbeiten" und "Deaktivieren" |

**Button "Bearbeiten"** → `/provider/scooters/<uid>/edit`
**Button "Deaktivieren"** → POST `/provider/scooters/<uid>/delete`
**Button "Neuen Scooter hinzufügen"** → `/provider/scooters/add`

---

### 4.3 Scooter hinzufügen – `/provider/scooters/add` (GET/POST)

**Zweck:** Neuen Scooter für den Provider anlegen

**Seitenelemente (GET):**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| Fahrzeugtyp | Dropdown | Ja | Alle `VehicleType`-Einträge aus DB |
| Modell | Textfeld | Ja | Max. 100 Zeichen (z.B. "Xiaomi Pro 2") |
| Batterie (%) | Zahlenfeld | Ja | 0–100 |
| Status | Dropdown | Ja | available / maintenance / disabled |
| **Leaflet-Karte** | Interaktiv | Nein | Klick auf Karte setzt Standort-Marker |
| Latitude | Zahlenfeld | Nein | Wird automatisch aus Karte befüllt |
| Longitude | Zahlenfeld | Nein | Wird automatisch aus Karte befüllt |
| Speichern | Submit-Button | – | – |

**Backend-Logik (POST):**
1. Formular validiert
2. Neues `Scooter`-Objekt:
   - `uid` = neue UUID
   - `uid_provider` = `current_user.uid`
   - `vehicle_type_uid` = aus Formular
   - `model` = aus Formular
   - `qr_code` = zufällig generierter UUID-String (eindeutig)
   - `status` = aus Formular
   - `battery_level` = aus Formular
   - `latitude`, `longitude` = aus Formular (oder NULL)
   - `gefahrene_km_gesamt` = 0
   - `created_at` = aktueller Zeitstempel
3. Gespeichert in `scooters`
4. Flash: "Scooter erfolgreich hinzugefügt."
5. **Redirect:** → `/provider/scooters`

---

### 4.4 Scooter bearbeiten – `/provider/scooters/<uid>/edit` (GET/POST)

**Zweck:** Bestehenden Scooter des Providers editieren

**Seitenelemente (GET):**
- Identisches Formular wie "Scooter hinzufügen"
- Felder sind mit aktuellen Werten des Scooters vorbelegt
- Karte zeigt aktuellen Standort-Marker

**Zugriffschutz:**
- `scooter.uid_provider` muss `current_user.uid` entsprechen → sonst 403

**Backend-Logik (POST):**
1. Scooter-Felder mit Formular-Werten aktualisiert
2. Wenn Status auf "maintenance" gesetzt und vorher nicht maintenance: `maintenance_since = datetime.utcnow()`
3. Wenn Status von "maintenance" auf anderen Status: `maintenance_since = NULL`
4. Gespeichert in `scooters`
5. Flash: "Scooter aktualisiert."
6. **Redirect:** → `/provider/scooters`

---

### 4.5 Scooter deaktivieren – `/provider/scooters/<uid>/delete` (POST)

**Zweck:** Scooter aus dem Angebot nehmen (Soft-Delete)

**Backend-Logik:**
1. Scooter muss `uid_provider = current_user.uid` haben → sonst 403
2. Scooter darf nicht Status "rented" haben → sonst Flash-Fehler
3. `scooter.status = 'disabled'`
4. Gespeichert
5. Flash: "Scooter deaktiviert."
6. **Redirect:** → `/provider/scooters`

---

### 4.6 Tarife ansehen – `/provider/tariffs` (GET)

**Zweck:** Übersicht der geltenden Tarife pro Fahrzeugtyp

**Seitenelemente:**

**Aktive Tarife (Karten je Fahrzeugtyp):**

| Element | Inhalt |
|---------|--------|
| Fahrzeugtyp | `vehicle_type.name` |
| Grundpreis | `tarif.base_price` CHF |
| Minutenpreis | `tarif.minute_price` CHF/min |
| Gültig ab | `tarif.valid_from` |

**Historische Tarif-Tabelle:**

| Spalte | Inhalt |
|--------|--------|
| Fahrzeugtyp | `vehicle_type.name` |
| Grundpreis | `base_price` |
| Minutenpreis | `minute_price` |
| Gültig von | `valid_from` |
| Gültig bis | `valid_to` (oder "–" wenn noch aktiv) |
| Status | "Aktiv" / "Abgelaufen" |

**Backend-Logik:**
- `VehicleType.with_active_tariffs()` gibt alle Fahrzeugtypen mit ihrem aktuellen aktiven Tarif zurück
- Alle Tarife sortiert nach `valid_from DESC`

---

## 5. Rolle: Administrator (admin)

### 5.1 Admin-Dashboard – `/admin/dashboard` (GET)

**Zweck:** Systemweite Übersicht

**Seitenelemente:**

**Statistik-Karten:**

| Karte | Inhalt | Quelle |
|-------|--------|--------|
| Benutzer | Anzahl User mit Rolle "user" | `users` WHERE `user_rolle='user'` |
| Anbieter | Anzahl User mit Rolle "provider" | `users` WHERE `user_rolle='provider'` |
| Scooter gesamt | Alle Scooter (ausser disabled) | `scooters` |
| Aktive Fahrten | Fahrten ohne Endzeit | `rides` WHERE `endzeit IS NULL` |
| Gesamtumsatz | Summe aller completed Transaktionen | `Transaction.total_revenue()` |
| Aktive Tarife | Anzahl aktiver Tarife | `tariffs` WHERE `is_active=True` |

**Quick-Links zu allen Admin-Bereichen:**
- Benutzer verwalten → `/admin/users`
- Scooter verwalten → `/admin/scooters`
- Fahrten → `/admin/rides`
- Transaktionen → `/admin/transactions`
- Fahrzeugtypen → `/admin/vehicle-types`
- Tarife → `/admin/tariffs`

---

### 5.2 Benutzerliste – `/admin/users` (GET)

**Zweck:** Alle Benutzer anzeigen und filtern

**Seitenelemente:**

**Filter-Tabs:**
- "Alle" | "Fahrer" | "Anbieter" | "Admin"
- URL-Parameter `?role=user` / `?role=provider` / `?role=admin`

**Benutzer-Tabelle:**

| Spalte | Inhalt |
|--------|--------|
| Name | `vorname nachname` |
| Benutzername | `username` |
| E-Mail | `email` |
| Rolle | Farbiges Badge (user/provider/admin) |
| Status | "Aktiv" (grün) / "Deaktiviert" (rot) |
| Erstellt | `created_at` formatiert |
| Letzter Login | `last_login` formatiert |
| Aktionen | Button "Details" + Button "Aktivieren/Deaktivieren" |

**Button "Details"** → `/admin/users/<uid>`
**Button "Aktivieren/Deaktivieren"** → POST `/admin/users/<uid>/toggle-status`

---

### 5.3 Benutzerdetail – `/admin/users/<uid>` (GET)

**Zweck:** Einzelnen Benutzer und seine Relationen anzeigen

**Seitenelemente:**

**Benutzer-Informationskarte:**

| Feld | Inhalt |
|------|--------|
| Name | `vorname nachname` |
| Benutzername | `username` |
| E-Mail | `email` |
| Rolle | Badge |
| Status | Badge |
| Erstellt | `created_at` |
| Letzter Login | `last_login` |

**Für Fahrer (Rolle "user"):**
- Tabelle der letzten 10 Fahrten (Datum, Scooter, Dauer, KM, Preis)
- Link zu jeder Fahrt → `/admin/rides/<ride_uid>`

**Für Anbieter (Rolle "provider"):**
- Tabelle aller Scooter des Anbieters (Modell, Typ, Status, Batterie)
- Link zu Scooter-Detail

**Button "Status umschalten"** → POST `/admin/users/<uid>/toggle-status`

---

### 5.4 Benutzer aktivieren/deaktivieren – `/admin/users/<uid>/toggle-status` (POST)

**Backend-Logik:**
1. Admins können nicht deaktiviert werden → Flash-Fehler
2. `user.status = 'deactivated'` wenn aktiv, `'active'` wenn deaktiviert
3. Gespeichert in `users`
4. Flash: "Benutzer aktiviert." / "Benutzer deaktiviert."
5. **Redirect:** → `/admin/users`

---

### 5.5 Scooter-Liste (Admin) – `/admin/scooters` (GET)

**Zweck:** Alle Scooter systemweit anzeigen und filtern

**Seitenelemente:**

**Filter-Tabs:**
- "Alle" | "Verfügbar" | "Vermietet" | "Wartung" | "Deaktiviert"
- URL-Parameter `?status=available` etc.

**Scooter-Tabelle:**

| Spalte | Inhalt |
|--------|--------|
| Modell | `scooter.model` |
| Fahrzeugtyp | `vehicle_type.name` |
| Anbieter | `provider.username` |
| Status | Farbiges Badge |
| Batterie | `battery_level`% |
| Standort | Koordinaten |
| Erstellt | `created_at` |
| Aktionen | Button "Status umschalten" |

**Button "Status umschalten"** → POST `/admin/scooters/<uid>/toggle-status`

---

### 5.6 Scooter-Status umschalten – `/admin/scooters/<uid>/toggle-status` (POST)

**Backend-Logik:**
1. Scooter darf nicht Status "rented" haben → sonst Flash-Fehler
2. `'available'` → `'disabled'`, `'disabled'` → `'available'`, `'maintenance'` → `'available'`
3. Gespeichert
4. Flash: entsprechend
5. **Redirect:** → `/admin/scooters`

---

### 5.7 Fahrten-Liste (Admin) – `/admin/rides` (GET)

**Zweck:** Alle Fahrten systemweit anzeigen und filtern

**Seitenelemente:**

**Filter-Tabs:**
- "Alle" | "Aktiv" | "Abgeschlossen"
- URL-Parameter `?status=active` / `?status=completed`

**Fahrten-Tabelle:**

| Spalte | Inhalt |
|--------|--------|
| Datum | `startzeit` |
| Fahrer | `rider.username` |
| Scooter | `scooter.model` |
| Dauer | `duration_str` (bei aktiven: laufend) |
| KM | `gefahrene_km` (oder "–" wenn aktiv) |
| Preis | `gesamtpreis` CHF (oder "aktiv") |
| Status | "Aktiv" / "Abgeschlossen" |
| Detail | Link → `/admin/rides/<uid>` |

---

### 5.8 Fahrtdetail (Admin) – `/admin/rides/<uid>` (GET)

**Zweck:** Vollständige Fahrt- und Transaktionsinformation

**Seitenelemente:**

**Fahrt-Informationen:**
- Fahrer (Link → `/admin/users/<uid>`)
- Scooter-Modell und Fahrzeugtyp
- Startzeit, Endzeit, Dauer
- Gefahrene KM
- Gesamtpreis
- Angew. Tarif (Grundpreis + Minutenpreis)

**Transaktions-Informationen:**
- Betrag
- Status (completed/pending/failed)
- Verwendete Zahlungsmethode (maskiert)
- Erstellt am

---

### 5.9 Transaktionen – `/admin/transactions` (GET)

**Zweck:** Alle Transaktionen systemweit mit Umsatzübersicht

**Seitenelemente:**

**Umsatz-Karte (oben):**
- Gesamtumsatz aller "completed" Transaktionen in CHF

**Filter-Tabs:**
- "Alle" | "Abgeschlossen" | "Ausstehend" | "Fehlgeschlagen"
- URL-Parameter `?status=completed` / `?status=pending` / `?status=failed`

**Transaktions-Tabelle:**

| Spalte | Inhalt |
|--------|--------|
| Datum | `created_at` |
| Fahrer | `ride.rider.username` |
| Fahrt | Link → `/admin/rides/<uid>` |
| Betrag | `betrag` CHF |
| Status | Farbiges Badge |
| Zahlungsmethode | `kartenidentifier_maskiert` |

---

### 5.10 Fahrzeugtypen – `/admin/vehicle-types` (GET/POST)

**Zweck:** Fahrzeugtypen anlegen und verwalten

**Seitenelemente:**

**Liste bestehender Fahrzeugtypen (Tabelle):**

| Spalte | Inhalt |
|--------|--------|
| Name | `vehicle_type.name` |
| Beschreibung | `vehicle_type.description` |
| Geschwindigkeit | `meter_per_minute` m/min |
| Akkuverbrauch | `battery_drain_per_minute` %/min |
| Ladegeschwindigkeit | `battery_charge_per_minute` %/min |
| Scooter-Anzahl | Anzahl Scooter mit diesem Typ |
| Aktionen | "Bearbeiten" + "Löschen" |

**Button "Bearbeiten"** → `/admin/vehicle-types/<uid>/edit`
**Button "Löschen"** → POST `/admin/vehicle-types/<uid>/delete`

**Formular "Neuen Fahrzeugtyp anlegen" (inline):**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| Name | Textfeld | Ja | Eindeutig, max. 100 Zeichen (z.B. "Standard Scooter") |
| Beschreibung | Textfeld | Nein | Max. 255 Zeichen |
| Meter pro Minute | Zahlenfeld | Ja | Simulierte Geschwindigkeit (z.B. 250 = 15 km/h) |
| Akkuverbrauch/Min | Dezimalfeld | Ja | Prozent pro Minute (z.B. 0.5) |
| Ladegeschw./Min | Dezimalfeld | Ja | Prozent pro Minute (z.B. 1.0) |
| Anlegen | Submit-Button | – | – |

**Backend-Logik (POST – Neu):**
1. Formular validiert
2. Name auf Eindeutigkeit geprüft → sonst Flash-Fehler
3. Neues `VehicleType`-Objekt in `vehicle_types` gespeichert
4. Flash: "Fahrzeugtyp erstellt."
5. **Redirect:** → `/admin/vehicle-types`

---

### 5.11 Fahrzeugtyp bearbeiten – `/admin/vehicle-types/<uid>/edit` (GET/POST)

**Zweck:** Bestehenden Fahrzeugtyp bearbeiten

**Seitenelemente (GET):**
- Formular mit vorausgefüllten Werten (identisch mit Anlegen-Formular)

**Backend-Logik (POST):**
1. Felder aktualisiert
2. Gespeichert in `vehicle_types`
3. Flash: "Fahrzeugtyp aktualisiert."
4. **Redirect:** → `/admin/vehicle-types`

---

### 5.12 Fahrzeugtyp löschen – `/admin/vehicle-types/<uid>/delete` (POST)

**Backend-Logik:**
1. Prüfung: Scooter mit diesem Typ vorhanden → Flash-Fehler, kein Löschen
2. Prüfung: Tarife mit diesem Typ vorhanden → Flash-Fehler, kein Löschen
3. `db.session.delete(vehicle_type)`
4. Gespeichert
5. Flash: "Fahrzeugtyp gelöscht."
6. **Redirect:** → `/admin/vehicle-types`

---

### 5.13 Tarife (Admin) – `/admin/tariffs` (GET/POST)

**Zweck:** Tarife je Fahrzeugtyp verwalten

**Seitenelemente:**

**Aktive Tarife (Karten je Fahrzeugtyp):**
- Verwendet Makro `active_tariffs_list()` aus `macros.html`
- Zeigt pro Fahrzeugtyp: Name, Grundpreis, Minutenpreis, Gültig ab

**Alle Tarife (Tabelle):**

| Spalte | Inhalt |
|--------|--------|
| Fahrzeugtyp | `vehicle_type.name` |
| Grundpreis | `base_price` CHF |
| Minutenpreis | `minute_price` CHF/min |
| Gültig von | `valid_from` |
| Gültig bis | `valid_to` (oder "–") |
| Status | "Aktiv" (grün) / "Abgelaufen" (grau) |

**Formular "Neuen Tarif anlegen":**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| Fahrzeugtyp | Dropdown | Ja | Alle `VehicleType`-Einträge |
| Grundpreis | Dezimalfeld | Ja | CHF, z.B. 1.00 |
| Minutenpreis | Dezimalfeld | Ja | CHF/min, z.B. 0.25 |
| Gültig ab | Datumsfeld | Ja | Ab welchem Datum gültig |
| Anlegen | Submit-Button | – | – |

**Backend-Logik (POST):**
1. Formular validiert
2. Bestehender aktiver Tarif für diesen Fahrzeugtyp:
   - `is_active = False`
   - `valid_to = valid_from des neuen Tarifs - 1 Tag` (wird automatisch gesetzt)
3. Neuer `Tariff`-Eintrag:
   - `uid` = neue UUID
   - `vehicle_type_uid` = aus Formular
   - `base_price`, `minute_price`, `valid_from` = aus Formular
   - `valid_to` = NULL (kein Enddatum)
   - `is_active` = True
4. Gespeichert in `tariffs`
5. Flash: "Tarif erstellt."
6. **Redirect:** → `/admin/tariffs`

---

## 6. REST-API (technisch)

Alle API-Endpunkte sind unter dem Prefix `/api` erreichbar.
Authentifizierung via **JWT Bearer Token** im Header: `Authorization: Bearer <token>`

### 6.1 Login – POST `/api/auth/login`

**Request (JSON):**
```json
{ "username": "user1", "password": "geheim123" }
```

**Response (200):**
```json
{ "access_token": "eyJ..." }
```

**Fehler:**
- 401: Ungültige Zugangsdaten

---

### 6.2 Scooter-Liste – GET `/api/scooters`

**Authentifizierung:** Keine (public)

**Response (200):**
```json
[
  {
    "uid": "...",
    "model": "Xiaomi Pro 2",
    "status": "available",
    "battery_level": 85,
    "latitude": 47.376,
    "longitude": 8.541,
    "vehicle_type": "Standard Scooter"
  }
]
```

---

### 6.3 Einzelner Scooter – GET `/api/scooters/<uid>`

**Authentifizierung:** Keine (public)

**Response:** Einzelnes Scooter-Objekt (wie oben)

**Fehler:** 404 wenn nicht gefunden

---

### 6.4 Scooter anlegen – POST `/api/scooters`

**Authentifizierung:** JWT, Rolle "provider"

**Request (JSON):**
```json
{
  "model": "Segway Ninebot",
  "vehicle_type_uid": "...",
  "battery_level": 100,
  "latitude": 47.376,
  "longitude": 8.541
}
```

**Response (201):** Erstelltes Scooter-Objekt

---

### 6.5 Eigene Fahrten – GET `/api/rides`

**Authentifizierung:** JWT, Rolle "user"

**Response:** Liste der abgeschlossenen Fahrten des eingeloggten Users

---

### 6.6 Einzelne Fahrt – GET `/api/rides/<uid>`

**Authentifizierung:** JWT, Rolle "user"

**Sicherheit:** Nur eigene Fahrten abrufbar (uid_rider muss übereinstimmen)

**Response:** Einzelnes Ride-Objekt

---

### 6.7 Aktiver Tarif – GET `/api/tariffs/active`

**Authentifizierung:** Keine (public)

**Response:** Aktiver Tarif (pro Fahrzeugtyp oder erster aktiver)

---

### 6.8 Eigene Transaktionen – GET `/api/transactions`

**Authentifizierung:** JWT, Rolle "user"

**Response:** Liste eigener Transaktionen mit Beträgen und Status

---

### API-Fehlerantworten (JSON)

| Fehler | HTTP-Status | Beschreibung |
|--------|-------------|--------------|
| Kein Token | 401 | `{"msg": "Missing Authorization Header"}` |
| Token abgelaufen | 401 | `{"msg": "Token has expired"}` |
| Ungültiger Token | 422 | `{"msg": "Signature verification failed"}` |
| Keine Berechtigung | 403 | `{"msg": "Zugriff verweigert"}` |

---

## 7. Fehlerseiten

### 403 – Forbidden (`/errors/403.html`)
- Angezeigt bei unberechtigtem Zugriff (falsche Rolle, fremde Ressource)
- Button "Zurück zur Startseite" → `/`

### 404 – Not Found (`/errors/404.html`)
- Angezeigt bei nicht gefundenen Routen oder Ressourcen
- Button "Zurück zur Startseite" → `/`

---

## Anhang: Datenbankschema-Übersicht

```
users
 └──< rides (rider_uid)
 └──< payment_methods (rider_uid)
 └──< scooters (uid_provider)

vehicle_types
 └──< scooters (vehicle_type_uid)
 └──< tariffs (vehicle_type_uid)

scooters
 └──< rides (scooter_uid)

tariffs
 └──< rides (tarif_uid)

rides
 └──< transactions (ride_uid)

payment_methods
 └──< transactions (payment_method_uid)
```

---

## Anhang: Status-Definitionen

### Scooter-Status

| Status | Farbe | Bedeutung |
|--------|-------|-----------|
| `available` | Grün | Bereit zur Miete |
| `rented` | Blau | Aktuell vermietet |
| `maintenance` | Orange | In Wartung |
| `disabled` | Rot | Deaktiviert (Soft-Delete) |

### User-Status

| Status | Bedeutung |
|--------|-----------|
| `active` | Konto aktiv, Login möglich |
| `deactivated` | Konto gesperrt, Login verweigert |

### Transaktions-Status

| Status | Bedeutung |
|--------|-----------|
| `completed` | Zahlung erfolgreich |
| `pending` | Ausstehend |
| `failed` | Fehlgeschlagen |

---

## Anhang: Benutzerrollen und Zugriffsmatrix

| Bereich | user | provider | admin |
|---------|------|----------|-------|
| `/dashboard` | ✓ | – | – |
| `/scooters` | ✓ | – | – |
| `/rides/*` | ✓ | – | – |
| `/payment-methods` | ✓ | – | – |
| `/provider/*` | – | ✓ | – |
| `/admin/*` | – | – | ✓ |
| `/api/scooters` (GET) | ✓ | ✓ | ✓ |
| `/api/scooters` (POST) | – | ✓ | – |
| `/api/rides` | ✓ | – | – |
| `/api/transactions` | ✓ | – | – |
