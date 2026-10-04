# Registriert die Azure Resource Provider, die dieses Projekt braucht.
# Idempotent: bereits registrierte Provider werden einfach übersprungen.
# Vor "terraform apply" einmal ausführen (nach "az login").

$providers = @(
    "Microsoft.Sql",                  # Azure SQL Database (DBaaS)
    "Microsoft.App",                  # Azure Container Apps
    "Microsoft.OperationalInsights"   # Log Analytics (Logs der Container App)
)

foreach ($p in $providers) {
    Write-Host "Registriere $p ..."
    az provider register --namespace $p --wait
}

Write-Host "Fertig. Weiter mit: cd terraform; terraform init; terraform apply"
