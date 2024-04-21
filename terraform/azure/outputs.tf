output "resource_group_name" {
  value = data.azurerm_resource_group.rg.name
}

output "public_ip_address" {
  value = azurerm_linux_virtual_machine.datalab_vm.public_ip_address
}
