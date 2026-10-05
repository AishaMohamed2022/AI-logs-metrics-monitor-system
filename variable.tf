
variable "ami_id" {
  description = "AMI ID used for EC2 instances"
  type        = string
  default     = "ami-12345678"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}