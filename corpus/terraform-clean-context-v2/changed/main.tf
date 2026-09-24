terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

variable "security_group_id" {
  type = string
}

variable "admin_cidr" {
  type    = string
  default = "10.20.0.0/16"
  validation {
    condition     = contains(["10.20.0.0/16", "10.30.0.0/16"], var.admin_cidr)
    error_message = "Admin access must use an approved private CIDR."
  }
}

resource "aws_security_group_rule" "admin" {
  type              = "ingress"
  security_group_id = var.security_group_id
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [var.admin_cidr]
}
