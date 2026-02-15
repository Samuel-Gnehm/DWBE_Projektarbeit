-- SQL Server Schema basierend auf docs/SQL_DataModel.md
CREATE TABLE users (
    UID UNIQUEIDENTIFIER NOT NULL,
    Vorname NVARCHAR(100) NOT NULL,
    Nachname NVARCHAR(100) NOT NULL,
    Username NVARCHAR(50) NOT NULL,
    Email NVARCHAR(255) NOT NULL,
    Passwort_Hash NVARCHAR(255) NOT NULL,
    User_Rolle NVARCHAR(20) NOT NULL,
    Status NVARCHAR(20) NOT NULL,
    Last_Login DATETIME2 NULL,
    Created_At DATETIME2 NOT NULL,
    CONSTRAINT PK_users PRIMARY KEY (UID),
    CONSTRAINT UQ_users_Username UNIQUE (Username),
    CONSTRAINT UQ_users_Email UNIQUE (Email)
);

CREATE TABLE tariffs (
    UID UNIQUEIDENTIFIER NOT NULL,
    Base_Price DECIMAL(10,2) NOT NULL,
    Minute_Price DECIMAL(10,2) NOT NULL,
    Valid_From DATE NOT NULL,
    Valid_To DATE NULL,
    Is_Active BIT NOT NULL,
    CONSTRAINT PK_tariffs PRIMARY KEY (UID)
);

CREATE TABLE scooters (
    UID UNIQUEIDENTIFIER NOT NULL,
    UID_Provider UNIQUEIDENTIFIER NOT NULL,
    Model NVARCHAR(100) NOT NULL,
    Status NVARCHAR(20) NOT NULL,
    GefahreneKM_Gesamt DECIMAL(10,2) NOT NULL,
    Battery_Level TINYINT NOT NULL,
    Latitude DECIMAL(9,6) NOT NULL,
    Longitude DECIMAL(9,6) NOT NULL,
    Created_At DATETIME2 NOT NULL,
    CONSTRAINT PK_scooters PRIMARY KEY (UID),
    CONSTRAINT FK_scooters_UID_Provider_users_UID FOREIGN KEY (UID_Provider)
        REFERENCES users(UID)
);

CREATE TABLE rides (
    UID UNIQUEIDENTIFIER NOT NULL,
    Rider_UID UNIQUEIDENTIFIER NOT NULL,
    Scooter_UID UNIQUEIDENTIFIER NOT NULL,
    Tarif_UID UNIQUEIDENTIFIER NOT NULL,
    Startzeit DATETIME2 NOT NULL,
    Endzeit DATETIME2 NULL,
    Gesamtpreis DECIMAL(10,2) NOT NULL,
    GefahreneKM DECIMAL(10,2) NOT NULL,
    Created_At DATETIME2 NOT NULL,
    CONSTRAINT PK_rides PRIMARY KEY (UID),
    CONSTRAINT FK_rides_Rider_UID_users_UID FOREIGN KEY (Rider_UID)
        REFERENCES users(UID),
    CONSTRAINT FK_rides_Scooter_UID_scooters_UID FOREIGN KEY (Scooter_UID)
        REFERENCES scooters(UID),
    CONSTRAINT FK_rides_Tarif_UID_tariffs_UID FOREIGN KEY (Tarif_UID)
        REFERENCES tariffs(UID)
);

CREATE TABLE payment_methods (
    UID UNIQUEIDENTIFIER NOT NULL,
    Rider_UID UNIQUEIDENTIFIER NOT NULL,
    Kartenidentifier_Maskiert NVARCHAR(25) NOT NULL,
    Is_Active BIT NOT NULL,
    Created_At DATETIME2 NOT NULL,
    CONSTRAINT PK_payment_methods PRIMARY KEY (UID),
    CONSTRAINT FK_payment_methods_Rider_UID_users_UID FOREIGN KEY (Rider_UID)
        REFERENCES users(UID)
);

