# Independent portfolio demo - hub-and-spoke environment for a fictional
# asset-management platform. Validate-only by default; nothing is deployed
# unless you run `terraform apply` against your own subscription.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
  }
  # Example remote state (commented so `terraform init -backend=false` works):
  # backend "azurerm" {
  #   resource_group_name  = "rg-tfstate-demo"
  #   storage_account_name = "sttfstatedemo001"
  #   container_name       = "tfstate"
  #   key                  = "assetmgmt-hub-spoke.tfstate"
  # }
}

provider "azurerm" {
  features {}
}

locals {
  # Mandatory tags applied to every resource (enforce with Azure Policy too).
  tags = merge({
    application = "assetmgmt-demo"
    environment = var.environment
    owner       = var.owner
    cost_centre = var.cost_centre
    data_class  = "synthetic"
    managed_by  = "terraform"
  }, var.extra_tags)

  name_prefix = "${var.workload}-${var.environment}"
}

resource "azurerm_resource_group" "hub" {
  name     = "rg-${local.name_prefix}-hub"
  location = var.location
  tags     = local.tags
}

resource "azurerm_resource_group" "spoke" {
  for_each = var.spokes
  name     = "rg-${local.name_prefix}-${each.key}"
  location = var.location
  tags     = local.tags
}

resource "azurerm_log_analytics_workspace" "hub" {
  name                = "log-${local.name_prefix}"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days
  daily_quota_gb      = var.log_daily_cap_gb # cost guard-rail
  tags                = local.tags
}
