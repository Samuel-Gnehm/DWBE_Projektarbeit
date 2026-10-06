# E-Scooter-Verleihplattform: Cloud-Deployment (VICC Praxisarbeit)

Dieses Repo enthält die Flask-App und die Infrastruktur, um sie auf Azure
(Container Apps + Azure SQL Database) bereitzustellen.

## Voraussetzungen
- Azure-Subscription, Azure CLI (`az login`), Terraform
- Docker nur nötig, wenn das Image selbst gebaut werden soll. Das fertige
  Image liegt öffentlich auf Docker Hub (`samuelgnehm/scooter-app`).

## Nachbauen
```powershell
az login
.\scripts\bootstrap.ps1          # oder: sh scripts/bootstrap.sh
cd terraform
copy terraform.tfvars.example terraform.tfvars   # Werte eintragen
terraform init
terraform apply
```
`terraform output app_url` zeigt die URL der App. Beim Containerstart laufen
automatisch die DB-Migrationen und das Anlegen des Admin-Users (`entrypoint.sh`).

## Wichtig bei den Variablen
- `unique_suffix`: der SQL-Servername muss weltweit eindeutig sein, bitte ein eigenes Kürzel wählen.
- `location`: manche Subscriptions (z.B. Azure for Students) erlauben nur bestimmte Regionen.
  Erlaubte Regionen abfragen mit:
  `az policy assignment list --query "[?parameters.listOfAllowedLocations.value!=null].parameters.listOfAllowedLocations.value[]" -o tsv`
- `docker_image`: Standard ist das öffentliche Image, kein eigener Build nötig.

## Struktur
- `app/`: Flask-Anwendung (Web-UI und JSON-API unter `/api`)
- `Dockerfile`, `entrypoint.sh`: Container-Image
- `terraform/`: Azure-Infrastruktur als Code
- `scripts/`: Bootstrap (Registrierung der Azure Resource Provider)
