resource "aws_instance" "pub_1" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public_subnet_01.id

  vpc_security_group_ids = [
    aws_security_group.public_alb_sg.id
  ]

  tags = {
    Name = "EC2-pub-1"
  }
}

resource "aws_instance" "private_1" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.private_subnet_01.id

  vpc_security_group_ids = [
    aws_security_group.public_alb_sg.id
  ]

  tags = {
    Name = "EC2-private-1"
  }
}

resource "aws_instance" "pub_2" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public_subnet_02.id

  vpc_security_group_ids = [
    aws_security_group.public_alb_sg.id
  ]

  tags = {
    Name = "EC2-pub-2"
  }
}

resource "aws_instance" "private_2" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.private_subnet_02.id

  vpc_security_group_ids = [
    aws_security_group.public_alb_sg.id
  ]

  tags = {
    Name = "EC2-private-2"
  }
}