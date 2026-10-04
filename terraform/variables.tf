variable "location" {
  type    = string
  default = "switzerlandnorth"
}

variable "unique_suffix" {
  description = "Kurzes eindeutiges Suffix, da Azure SQL Server-Namen global eindeutig sein müssen"
  type        = string
}

variable "sql_admin_user" {
  type    = string
  default = "sqladmin"
}

variable "sql_admin_password" {
  type      = string
  sensitive = true
}

variable "flask_secret_key" {
  type      = string
  sensitive = true
}

variable "jwt_secret_key" {
  type      = string
  sensitive = true
}

variable "docker_image" {
  description = "Container-Image auf Docker Hub (öffentlich)"
  type        = string
  default     = "samuelgnehm/scooter-app:v2"
}
