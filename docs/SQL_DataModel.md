# Datenbankschema – E-Scooter Plattform

## Tabellen

---

### User (users)

| Attribut      | Typ  | Datentyp (SQL Server) | Unique | Beschreibung                 |
| ------------- | ---- | --------------------- | ------ | ---------------------------- |
| UID           | PK   | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel              |
| Vorname       | ATTR | NVARCHAR(100)         | Nein   | Vorname des Users            |
| Nachname      | ATTR | NVARCHAR(100)         | Nein   | Nachname des Users           |
| Username      | ATTR | NVARCHAR(50)          | Ja     | Eindeutiger Benutzername     |
| Email         | ATTR | NVARCHAR(255)         | Ja     | Eindeutige E-Mail            |
| Passwort_Hash | ATTR | NVARCHAR(255)         | Nein   | Gehashter Passwortwert       |
| User_Rolle    | ATTR | NVARCHAR(20)          | Nein   | 'provider', 'user' oder 'admin' |
| Status        | ATTR | NVARCHAR(20)          | Nein   | 'active' oder 'deactivated'  |
| Last_Login    | ATTR | DATETIME2             | Nein   | Zeitpunkt des letzten Logins |
| Created_At    | ATTR | DATETIME2             | Nein   | Erstellungsdatum             |

---

### Scooter (scooters)

| Attribut           | Typ            | Datentyp (SQL Server) | Unique | Beschreibung                                     |
| ------------------ | -------------- | --------------------- | ------ | ------------------------------------------------ |
| UID                | PK             | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel                                  |
| UID_Provider       | FK → Users.UID | UNIQUEIDENTIFIER      | Nein   | Anbieter des Scooters                            |
| Model              | ATTR           | NVARCHAR(100)         | Nein   | Modellbezeichnung                                |
| QR_Code            | ATTR           | NVARCHAR(100)         | Ja     | Eindeutiger QR-Code-Identifier (simuliert)       |
| Status             | ATTR           | NVARCHAR(20)          | Nein   | 'available', 'rented', 'maintenance', 'disabled' |
| GefahreneKM_Gesamt | ATTR           | DECIMAL(10,2)         | Nein   | Gesamtkilometer                                  |
| Battery_Level      | ATTR           | TINYINT               | Nein   | Akkustand (0–100)                                |
| Latitude           | ATTR           | DECIMAL(9,6)          | Nein   | Geoposition                                      |
| Longitude          | ATTR           | DECIMAL(9,6)          | Nein   | Geoposition                                      |
| Created_At         | ATTR           | DATETIME2             | Nein   | Erstellungsdatum                                 |

> **Hinweis `QR_Code`:** Da das physische Scannen eines QR-Codes im Rahmen dieser Webanwendung nicht umsetzbar ist, wird der QR-Code als eindeutiger String (z. B. UUID-Format) gespeichert und die Entsperrung über die Weboberfläche simuliert (Button «Scooter entsperren»).

---

### Tarif (tariffs)

| Attribut     | Typ  | Datentyp (SQL Server) | Unique | Beschreibung           |
| ------------ | ---- | --------------------- | ------ | ---------------------- |
| UID          | PK   | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel        |
| Base_Price   | ATTR | DECIMAL(10,2)         | Nein   | Basispreis pro Fahrt   |
| Minute_Price | ATTR | DECIMAL(10,2)         | Nein   | Preis pro Minute       |
| Valid_From   | ATTR | DATE                  | Nein   | Gültig ab              |
| Valid_To     | ATTR | DATE (NULL)           | Nein   | Gültig bis (NULL = aktuell aktiv) |
| Is_Active    | ATTR | BIT                   | Nein   | Aktiver Tarif (1 = Ja) |

---

### Fahrt (rides)

| Attribut    | Typ               | Datentyp (SQL Server) | Unique | Beschreibung            |
| ----------- | ----------------- | --------------------- | ------ | ----------------------- |
| UID         | PK                | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel         |
| Rider_UID   | FK → Users.UID    | UNIQUEIDENTIFIER      | Nein   | Fahrer                  |
| Scooter_UID | FK → Scooters.UID | UNIQUEIDENTIFIER      | Nein   | Verwendeter Scooter     |
| Tarif_UID   | FK → Tariffs.UID  | UNIQUEIDENTIFIER      | Nein   | Verwendeter Tarif       |
| Startzeit   | ATTR              | DATETIME2             | Nein   | Startzeitpunkt          |
| Endzeit     | ATTR              | DATETIME2 (NULL)      | Nein   | Endzeitpunkt (NULL = Fahrt aktiv) |
| Gesamtpreis | ATTR              | DECIMAL(10,2) (NULL)  | Nein   | Berechneter Gesamtpreis |
| GefahreneKM | ATTR              | DECIMAL(10,2)         | Nein   | Gefahrene Kilometer     |
| Created_At  | ATTR              | DATETIME2             | Nein   | Erstellungsdatum        |

---

### Zahlungsmethode (payment_methods)

| Attribut                  | Typ            | Datentyp (SQL Server) | Unique | Beschreibung           |
| ------------------------- | -------------- | --------------------- | ------ | ---------------------- |
| UID                       | PK             | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel        |
| Rider_UID                 | FK → Users.UID | UNIQUEIDENTIFIER      | Nein   | Zugehöriger Nutzer     |
| Kartenidentifier_Maskiert | ATTR           | NVARCHAR(25)          | Nein   | Maskierte Kartennummer |
| Is_Active                 | ATTR           | BIT                   | Nein   | Aktivstatus            |
| Created_At                | ATTR           | DATETIME2             | Nein   | Erstellungsdatum       |

---

### Transaktion (transactions)

| Attribut           | Typ                         | Datentyp (SQL Server) | Unique | Beschreibung                          |
| ------------------ | --------------------------- | --------------------- | ------ | ------------------------------------- |
| UID                | PK                          | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel                       |
| Ride_UID           | FK → Rides.UID              | UNIQUEIDENTIFIER      | Nein   | Zugehörige Fahrt                      |
| PaymentMethod_UID  | FK → PaymentMethods.UID     | UNIQUEIDENTIFIER      | Nein   | Verwendete Zahlungsmethode            |
| Betrag             | ATTR                        | DECIMAL(10,2)         | Nein   | Abgerechneter Betrag                  |
| Status             | ATTR                        | NVARCHAR(20)          | Nein   | 'pending', 'completed', 'failed'      |
| Created_At         | ATTR                        | DATETIME2             | Nein   | Zeitpunkt der Transaktion             |

---

## Beziehungen

| Beziehung                       | Kardinalität |
| ------------------------------- | ------------ |
| User (Provider) → Scooters      | 1 : N        |
| User (Rider) → Rides            | 1 : N        |
| Scooter → Rides                 | 1 : N        |
| Tariff → Rides                  | 1 : N        |
| User → PaymentMethods           | 1 : N        |
| Ride → Transactions             | 1 : 1        |
| PaymentMethod → Transactions    | 1 : N        |