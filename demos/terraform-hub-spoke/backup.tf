# Backup and DR building blocks. See docs/dr-and-cost.md for the design.

resource "azurerm_recovery_services_vault" "primary" {
  name                         = "rsv-${local.name_prefix}-primary"
  location                     = var.location
  resource_group_name          = azurerm_resource_group.hub.name
  sku                          = "Standard"
  storage_mode_type            = var.backup_storage_redundancy # GeoRedundant enables cross-region restore
  cross_region_restore_enabled = var.backup_storage_redundancy == "GeoRedundant"
  soft_delete_enabled          = true
  tags                         = local.tags
}

resource "azurerm_backup_policy_vm" "daily" {
  name                = "bkpol-vm-daily"
  resource_group_name = azurerm_resource_group.hub.name
  recovery_vault_name = azurerm_recovery_services_vault.primary.name
  timezone            = "India Standard Time"

  backup {
    frequency = "Daily"
    time      = "01:00"
  }

  retention_daily {
    count = var.backup_daily_retention
  }

  retention_weekly {
    count    = 12
    weekdays = ["Sunday"]
  }

  retention_monthly {
    count    = 12
    weekdays = ["Sunday"]
    weeks    = ["First"]
  }
}

# Secondary-region resource group used as the Azure Site Recovery target.
resource "azurerm_resource_group" "dr" {
  count    = var.enable_dr ? 1 : 0
  name     = "rg-${local.name_prefix}-dr"
  location = var.dr_location
  tags     = merge(local.tags, { purpose = "disaster-recovery" })
}

resource "azurerm_recovery_services_vault" "dr" {
  count               = var.enable_dr ? 1 : 0
  name                = "rsv-${local.name_prefix}-asr"
  location            = var.dr_location
  resource_group_name = azurerm_resource_group.dr[0].name
  sku                 = "Standard"
  soft_delete_enabled = true
  tags                = merge(local.tags, { purpose = "disaster-recovery" })
}
