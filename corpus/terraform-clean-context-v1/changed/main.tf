variable "admin_cidr" {
  type    = string
  default = "10.20.0.0/16"
  validation {
    condition     = var.admin_cidr != "0.0.0.0/0"
    error_message = "Admin access cannot be public."
  }
}

resource "aws_security_group_rule" "admin" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = [var.admin_cidr]
}
