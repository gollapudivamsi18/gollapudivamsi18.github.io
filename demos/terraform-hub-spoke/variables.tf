variable "workload" {
  description = "Short workload name used in resource names"
  type        = string
  default     = "amdemo"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "uat", "prod"], var.environment)
    error_message = "environment must be dev, uat or prod."
  }
}

variable "location" {
  description = "Primary Azure region"
  type        = string
  default     = "centralindia"
}

variable "dr_location" {
  description = "Secondary region for disaster recovery"
  type        = string
  default     = "southindia"
}

variable "owner" {
  description = "Owning team (tag)"
  type        = string
  default     = "platform-team"
}

variable "cost_centre" {
  description = "Cost centre (tag)"
  type        = string
  default     = "CC-0000-DEMO"
}

variable "extra_tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

variable "hub_address_space" {
  description = "Hub VNet CIDR"
  type        = string
  default     = "10.10.0.0/22"
}

variable "spokes" {
  description = "Spoke VNets keyed by short name"
  type = map(object({
    address_space = string
  }))
  default = {
    portfolio = { address_space = "10.11.0.0/24" }
    reporting = { address_space = "10.12.0.0/24" }
  }
}

variable "enable_gateway_transit" {
  description = "Set true once a VPN/ExpressRoute gateway exists in the hub"
  type        = bool
  default     = false
}

variable "log_retention_days" {
  type    = number
  default = 30
}

variable "log_daily_cap_gb" {
  description = "Daily ingestion cap for Log Analytics (cost guard-rail)"
  type        = number
  default     = 2
}

variable "backup_storage_redundancy" {
  description = "LocallyRedundant, ZoneRedundant or GeoRedundant"
  type        = string
  default     = "GeoRedundant"
}

variable "backup_daily_retention" {
  type    = number
  default = 14
}

variable "enable_dr" {
  description = "Create the secondary-region DR resource group and vault"
  type        = bool
  default     = false
}
