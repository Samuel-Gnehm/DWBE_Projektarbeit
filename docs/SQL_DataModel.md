**User (users)**
| Attribut      | Typ  | Datentyp (SQL Server) | Unique | Beschreibung                 |
| ------------- | ---- | --------------------- | ------ | ---------------------------- |
| UID           | PK   | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel              |
| Vorname       | ATTR | NVARCHAR(100)         | Nein   | Vorname des Users            |
| Nachname      | ATTR | NVARCHAR(100)         | Nein   | Nachname des Users           |
| Username      | ATTR | NVARCHAR(50)          | Ja     | Eindeutiger Benutzername     |
| Email         | ATTR | NVARCHAR(255)         | Ja     | Eindeutige E-Mail            |
| Passwort_Hash | ATTR | NVARCHAR(255)         | Nein   | Gehashter Passwortwert       |
| User_Rolle    | ATTR | NVARCHAR(20)          | Nein   | 'provider' oder 'user'       |
| Status        | ATTR | NVARCHAR(20)          | Nein   | 'active' oder 'deactivated'  |
| Last_Login    | ATTR | DATETIME2             | Nein   | Zeitpunkt des letzten Logins |
| Created_At    | ATTR | DATETIME2             | Nein   | Erstellungsdatum             |


**Scooter (scooters)**
| Attribut           | Typ            | Datentyp (SQL Server) | Unique | Beschreibung                                     |
| ------------------ | -------------- | --------------------- | ------ | ------------------------------------------------ |
| UID                | PK             | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel                                  |
| UID_Provider       | FK → Users.UID | UNIQUEIDENTIFIER      | Nein   | Anbieter des Scooters                            |
| Model              | ATTR           | NVARCHAR(100)         | Nein   | Modellbezeichnung                                |
| Status             | ATTR           | NVARCHAR(20)          | Nein   | 'available', 'rented', 'maintenance', 'disabled' |
| GefahreneKM_Gesamt | ATTR           | DECIMAL(10,2)         | Nein   | Gesamtkilometer                                  |
| Battery_Level      | ATTR           | TINYINT               | Nein   | Akkustand (0–100)                                |
| Latitude           | ATTR           | DECIMAL(9,6)          | Nein   | Geoposition                                      |
| Longitude          | ATTR           | DECIMAL(9,6)          | Nein   | Geoposition                                      |
| Created_At         | ATTR           | DATETIME2             | Nein   | Erstellungsdatum                                 |


**Tarif (tariffs)**
| Attribut     | Typ  | Datentyp (SQL Server) | Unique | Beschreibung           |
| ------------ | ---- | --------------------- | ------ | ---------------------- |
| UID          | PK   | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel        |
| Base_Price   | ATTR | DECIMAL(10,2)         | Nein   | Basispreis pro Fahrt   |
| Minute_Price | ATTR | DECIMAL(10,2)         | Nein   | Preis pro Minute       |
| Valid_From   | ATTR | DATE                  | Nein   | Gültig ab              |
| Valid_To     | ATTR | DATE (NULL)           | Nein   | Gültig bis             |
| Is_Active    | ATTR | BIT                   | Nein   | Aktiver Tarif (1 = Ja) |


**Fahrt (rides)**
| Attribut    | Typ               | Datentyp (SQL Server) | Unique | Beschreibung            |
| ----------- | ----------------- | --------------------- | ------ | ----------------------- |
| UID         | PK                | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel         |
| Rider_UID   | FK → Users.UID    | UNIQUEIDENTIFIER      | Nein   | Fahrer                  |
| Scooter_UID | FK → Scooters.UID | UNIQUEIDENTIFIER      | Nein   | Verwendeter Scooter     |
| Tarif_UID   | FK → Tariffs.UID  | UNIQUEIDENTIFIER      | Nein   | Verwendeter Tarif       |
| Startzeit   | ATTR              | DATETIME2             | Nein   | Startzeitpunkt          |
| Endzeit     | ATTR              | DATETIME2 (NULL)      | Nein   | Endzeitpunkt            |
| Gesamtpreis | ATTR              | DECIMAL(10,2)         | Nein   | Berechneter Gesamtpreis |
| GefahreneKM | ATTR              | DECIMAL(10,2)         | Nein   | Gefahrene Kilometer     |
| Created_At  | ATTR              | DATETIME2             | Nein   | Erstellungsdatum        |


**Zahlungsmethode (payment_methods)**
| Attribut                  | Typ            | Datentyp (SQL Server) | Unique | Beschreibung           |
| ------------------------- | -------------- | --------------------- | ------ | ---------------------- |
| UID                       | PK             | UNIQUEIDENTIFIER      | Ja     | Primärschlüssel        |
| Rider_UID                 | FK → Users.UID | UNIQUEIDENTIFIER      | Nein   | Zugehöriger Nutzer     |
| Kartenidentifier_Maskiert | ATTR           | NVARCHAR(25)          | Nein   | Maskierte Kartennummer |
| Is_Active                 | ATTR           | BIT                   | Nein   | Aktivstatus            |
| Created_At                | ATTR           | DATETIME2             | Nein   | Erstellungsdatum       |


**Beziehungen**
| Beziehung                  | Kardinalität |
| -------------------------- | ------------ |
| User (Provider) → Scooters | 1 : N        |
| User (Rider) → Rides       | 1 : N        |
| Scooter → Rides            | 1 : N        |
| Tariff → Rides             | 1 : N        |
| User → PaymentMethods      | 1 : N        |
