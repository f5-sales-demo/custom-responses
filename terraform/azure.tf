data "xcsh_network_regional_edges" "origin" {}

locals {
  tags = { project = "custom-responses", managed_by = "terraform" }
}
resource "azurerm_resource_group" "origin" {
  name     = "rg-custom-responses"
  location = "eastus2"
  tags     = local.tags
}
resource "azurerm_virtual_network" "origin" {
  name                = "vnet-custom-responses"
  location            = azurerm_resource_group.origin.location
  resource_group_name = azurerm_resource_group.origin.name
  address_space       = ["10.73.0.0/24"]
  tags                = local.tags
}
resource "azurerm_subnet" "origin" {
  name                 = "origin"
  resource_group_name  = azurerm_resource_group.origin.name
  virtual_network_name = azurerm_virtual_network.origin.name
  address_prefixes     = ["10.73.0.0/26"]
}
resource "azurerm_public_ip" "origin" {
  name                = "pip-custom-responses"
  location            = azurerm_resource_group.origin.location
  resource_group_name = azurerm_resource_group.origin.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = local.tags
}
resource "azurerm_network_security_group" "origin" {
  name                = "nsg-custom-responses"
  location            = azurerm_resource_group.origin.location
  resource_group_name = azurerm_resource_group.origin.name
  tags                = local.tags
  security_rule {
    name                       = "operator-ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.operator_cidr
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "xc-origin-listeners"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080-8084"
    source_address_prefixes    = concat(data.xcsh_network_regional_edges.origin.cidr_blocks, [var.operator_cidr])
    destination_address_prefix = "*"
  }
}
resource "azurerm_network_interface" "origin" {
  name                = "nic-custom-responses"
  location            = azurerm_resource_group.origin.location
  resource_group_name = azurerm_resource_group.origin.name
  tags                = local.tags
  ip_configuration {
    name                          = "origin"
    subnet_id                     = azurerm_subnet.origin.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.origin.id
  }
}
resource "azurerm_network_interface_security_group_association" "origin" {
  network_interface_id      = azurerm_network_interface.origin.id
  network_security_group_id = azurerm_network_security_group.origin.id
}
resource "azurerm_linux_virtual_machine" "origin" {
  name                            = "vm-custom-responses"
  location                        = azurerm_resource_group.origin.location
  resource_group_name             = azurerm_resource_group.origin.name
  size                            = "Standard_B2s"
  admin_username                  = "demo"
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.origin.id]
  tags                            = local.tags
  admin_ssh_key {
    username   = "demo"
    public_key = var.ssh_public_key
  }
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = 32
  }
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "22.04.202608060"
  }
  custom_data = base64encode(templatefile("${path.module}/cloud-init.yaml.tftpl", {
    panel         = base64encode(file("${path.module}/../origin/panel.html"))
    fixture       = base64encode(file("${path.module}/../origin/fixture.py"))
    inventory     = base64encode(file("${path.module}/.terraform/fixture-inventory.json"))
    httpbin_image = var.httpbin_image
  }))
  depends_on = [azurerm_network_interface_security_group_association.origin]
}
output "origin_ip" { value = azurerm_public_ip.origin.ip_address }
output "scenario_hosts" { value = [for s in jsondecode(file("${path.module}/../scenarios.json")) : s.hostname] }
