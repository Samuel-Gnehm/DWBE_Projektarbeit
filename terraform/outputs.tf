output "app_url" {
  value       = "https://${azurerm_container_app.app.ingress[0].fqdn}"
  description = "Browser-URL der App"
}

output "app_api_docs_hint" {
  value = "Web-API unter derselben Basis-URL, z.B. https://<fqdn>/api/... (je nach deinen Flask-Routen)"
}

output "sql_server_fqdn" {
  value = azurerm_mssql_server.sql.fully_qualified_domain_name
}
