# Hub VNet with shared services; each spoke peers only with the hub.

resource "azurerm_virtual_network" "hub" {
  name                = "vnet-${local.name_prefix}-hub"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  address_space       = [var.hub_address_space]
  tags                = local.tags
}

resource "azurerm_subnet" "hub_firewall" {
  name                 = "AzureFirewallSubnet" # name required by Azure
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub.name
  address_prefixes     = [cidrsubnet(var.hub_address_space, 2, 0)]
}

resource "azurerm_subnet" "hub_gateway" {
  name                 = "GatewaySubnet" # for a VPN/ExpressRoute gateway
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub.name
  address_prefixes     = [cidrsubnet(var.hub_address_space, 3, 2)]
}

resource "azurerm_subnet" "hub_shared" {
  name                 = "snet-shared-services"
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub.name
  address_prefixes     = [cidrsubnet(var.hub_address_space, 3, 3)]
}

resource "azurerm_virtual_network" "spoke" {
  for_each            = var.spokes
  name                = "vnet-${local.name_prefix}-${each.key}"
  location            = var.location
  resource_group_name = azurerm_resource_group.spoke[each.key].name
  address_space       = [each.value.address_space]
  tags                = local.tags
}

resource "azurerm_subnet" "spoke_app" {
  for_each             = var.spokes
  name                 = "snet-app"
  resource_group_name  = azurerm_resource_group.spoke[each.key].name
  virtual_network_name = azurerm_virtual_network.spoke[each.key].name
  address_prefixes     = [cidrsubnet(each.value.address_space, 1, 0)]
}

resource "azurerm_network_security_group" "spoke_app" {
  for_each            = var.spokes
  name                = "nsg-${local.name_prefix}-${each.key}-app"
  location            = var.location
  resource_group_name = azurerm_resource_group.spoke[each.key].name
  tags                = local.tags

  security_rule {
    name                       = "allow-https-from-hub"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = var.hub_address_space
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "deny-all-inbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "spoke_app" {
  for_each                  = var.spokes
  subnet_id                 = azurerm_subnet.spoke_app[each.key].id
  network_security_group_id = azurerm_network_security_group.spoke_app[each.key].id
}

resource "azurerm_virtual_network_peering" "hub_to_spoke" {
  for_each                  = var.spokes
  name                      = "peer-hub-to-${each.key}"
  resource_group_name       = azurerm_resource_group.hub.name
  virtual_network_name      = azurerm_virtual_network.hub.name
  remote_virtual_network_id = azurerm_virtual_network.spoke[each.key].id
  allow_forwarded_traffic   = true
  allow_gateway_transit     = var.enable_gateway_transit
}

resource "azurerm_virtual_network_peering" "spoke_to_hub" {
  for_each                  = var.spokes
  name                      = "peer-${each.key}-to-hub"
  resource_group_name       = azurerm_resource_group.spoke[each.key].name
  virtual_network_name      = azurerm_virtual_network.spoke[each.key].name
  remote_virtual_network_id = azurerm_virtual_network.hub.id
  allow_forwarded_traffic   = true
  use_remote_gateways       = var.enable_gateway_transit
}

resource "azurerm_private_dns_zone" "blob" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = azurerm_resource_group.hub.name
  tags                = local.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "spokes" {
  for_each              = var.spokes
  name                  = "link-${each.key}"
  resource_group_name   = azurerm_resource_group.hub.name
  private_dns_zone_name = azurerm_private_dns_zone.blob.name
  virtual_network_id    = azurerm_virtual_network.spoke[each.key].id
}
