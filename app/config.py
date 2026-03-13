import os


class Config:
    """Basisklasse – gemeinsame Einstellungen für alle Umgebungen."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Lokale Entwicklung – MSSQL via Windows-Authentifizierung."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class ProductionConfig(Config):
    """Produktion – MSSQL auf der Linux-VM der Schule."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
