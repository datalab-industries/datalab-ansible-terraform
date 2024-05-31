variable "resource_group_location" {
  type        = string
  default     = "northeurope"
  description = "Location of the resource group."
}

variable "username" {
  type        = string
  description = "The username for the local account that will be created on the new VM."
  default     = "azureadmin"
}

variable "resource_group_name" {
    type        = string
    description = "The name of the resource group in which the resources will be created."
}
