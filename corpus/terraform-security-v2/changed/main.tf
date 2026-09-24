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

resource "aws_security_group_rule" "admin" {
  type              = "ingress"
  security_group_id = var.security_group_id
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}
