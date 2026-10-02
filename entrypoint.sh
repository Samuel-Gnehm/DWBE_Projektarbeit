#!/bin/sh
set -e
 
echo "==> Führe ausstehende DB-Migrationen aus (flask db upgrade)..."
# Idempotent: Alembic prüft die aktuelle Revision in der DB (Tabelle
# alembic_version) und wendet nur an, was fehlt. Mehrfacher Aufruf beim
# Neustart/Scale-Out eines Containers ist deshalb ungefährlich, SOLANGE
# nicht mehrere Container beim allerersten Deploy gleichzeitig auf eine noch
# unversionierte DB treffen (siehe Hinweis in der Doku/Reflexion).
flask db upgrade
 
echo "==> Prüfe/erstelle Seed-Daten (idempotent, legt nur an falls nicht vorhanden)..."
python seed.py
 
echo "==> Starte Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 run:app