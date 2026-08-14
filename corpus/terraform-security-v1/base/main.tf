resource "aws_security_group_rule" "admin" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["10.20.0.0/16"]
}
