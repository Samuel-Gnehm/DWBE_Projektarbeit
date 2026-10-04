terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }
}

provider "azurerm" {
  features {}
  # Verhindert, dass Terraform bei jedem Lauf ~30 Azure Resource Provider
  # (auch ungenutzte) registrieren will. Bei Netzwerk-/Firewall-Problemen
  # bricht genau das mit "connection may have been reset" ab.
  # (skip_provider_registration ist die Syntax für azurerm-Provider v3.x,
  # das gepinnte required_providers-Version weiter oben im File)
  skip_provider_registration = true
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-scooter-vicc"
  location = var.location
}

# --- Azure SQL: Server + Serverless-Datenbank (Free-Tier-Grenzen: 100'000 vCore-Sekunden/Monat) ---

resource "azurerm_mssql_server" "sql" {
  name                         = "sql-scooter-vicc-${var.unique_suffix}"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_user
  administrator_login_password = var.sql_admin_password
  minimum_tls_version          = "1.2"
}

resource "azurerm_mssql_database" "db" {
  name                        = "scooter_db"
  server_id                   = azurerm_mssql_server.sql.id
  sku_name                    = "GP_S_Gen5_1" # General Purpose Serverless, Gen5, 1 vCore max
  min_capacity                = 0.5
  auto_pause_delay_in_minutes = 60 # pausiert nach 60min Inaktivität -> spart Kosten/Free-Tier-Budget
}

# Erlaubt Zugriff von anderen Azure-Diensten (Container Apps) auf den SQL-Server
resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.sql.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# --- Container Apps Environment + App ---

resource "azurerm_log_analytics_workspace" "logs" {
  name                = "log-scooter-vicc"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "env" {
  name                       = "cae-scooter-vicc"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
}

resource "azurerm_container_app" "app" {
  name                         = "ca-scooter-vicc"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"

  template {
    min_replicas = 0 # Scale-to-Zero in ruhigen Phasen -> Kernargument für die Skalierungs-Reflexion
    max_replicas = 5

    container {
      name   = "scooter-app"
      image  = var.docker_image
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "FLASK_ENV"
        value = "production"
      }
      env {
        name        = "SECRET_KEY"
        secret_name = "secret-key"
      }
      env {
        name        = "JWT_SECRET_KEY"
        secret_name = "jwt-secret-key"
      }
      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }
    }

    http_scale_rule {
      name                = "http-requests"
      concurrent_requests = 20
    }
  }

  secret {
    name  = "secret-key"
    value = var.flask_secret_key
  }
  secret {
    name  = "jwt-secret-key"
    value = var.jwt_secret_key
  }
  secret {
    name  = "database-url"
    value = "mssql+pymssql://${var.sql_admin_user}:${var.sql_admin_password}@${azurerm_mssql_server.sql.fully_qualified_domain_name}:1433/${azurerm_mssql_database.db.name}"
  }

  ingress {
    external_enabled = true
    target_port       = 5000
    transport         = "http"

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}
