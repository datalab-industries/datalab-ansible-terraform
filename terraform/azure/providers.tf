terraform {
  required_version = ">=0.12"
  required_providers {
    azapi = {
      source = "azure/azapi"
      version = "~>1.5,<1.13"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = false
}
