variable "subscription_id" { type = string }
variable "operator_cidr" {
  type = string
  validation {
    condition     = can(cidrhost(var.operator_cidr, 0)) && endswith(var.operator_cidr, "/32")
    error_message = "Restrict SSH to the operator IPv4 /32."
  }
}
variable "ssh_public_key" { type = string }
variable "httpbin_image" {
  type = string
  validation {
    condition     = can(regex("^mccutchen/go-httpbin@sha256:[a-f0-9]{64}$", var.httpbin_image))
    error_message = "Pin the verified httpbin digest."
  }
}
