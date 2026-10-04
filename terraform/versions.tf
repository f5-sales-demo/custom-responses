terraform {
  required_version = ">= 1.10.0, < 2.0.0"
  required_providers {
    xcsh    = { source = "f5-sales-demo/xcsh", version = "13.0.3" }
    azurerm = { source = "hashicorp/azurerm", version = "4.51.0" }
  }
  backend "local" {}
}
