#!/bin/sh
# Registriert die Azure Resource Provider, die dieses Projekt braucht.
# Idempotent: bereits registrierte Provider werden einfach übersprungen.
# Vor "terraform apply" einmal ausführen (nach "az login").
set -e

for p in Microsoft.Sql Microsoft.App Microsoft.OperationalInsights; do
  echo "Registriere $p ..."
  az provider register --namespace "$p" --wait
done

echo "Fertig. Weiter mit: cd terraform && terraform init && terraform apply"
