# Dockerfile für DWBE_Projektarbeit (E-Scooter-Verleihplattform)
#
# Wichtig: nutzt pymssql (FreeTDS) statt pyodbc, weil das im Container ohne
# Microsofts ODBC-Repo/Signierschlüssel auskommt -> kleineres, schnelleres Image,
# weniger Fehlerquellen unter Zeitdruck.
# Lokal unter Windows kannst du weiterhin pyodbc + trusted_connection nutzen,
# das betrifft nur die DATABASE_URL zur Laufzeit (siehe .env.production.example).

FROM python:3.11-slim

# FreeTDS für pymssql, gcc weil pymssql teils aus Source kompiliert wird
RUN apt-get update && apt-get install -y --no-install-recommends \
    freetds-dev \
    freetds-bin \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements zuerst kopieren -> Docker-Layer-Caching, schnellere Rebuilds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pymssql

COPY . .

ENV FLASK_ENV=production
# FLASK_APP nötig, damit "flask db upgrade" (Alembic/Flask-Migrate) die
# App-Factory findet -> current_app in migrations/env.py greift sonst ins Leere
ENV FLASK_APP=run.py
EXPOSE 5000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
