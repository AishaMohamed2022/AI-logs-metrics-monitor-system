# Application Load Balancer in the two public subnets
resource "aws_lb" "public_alb" {
  name               = "public-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.public_alb_sg.id]
  subnets = [
    aws_subnet.public_subnet_01.id,
    aws_subnet.public_subnet_02.id
  ]

  tags = {
    Name = "public-alb"
  }
}

# Target group (Node app assumed to listen on port 3000, so change if needed)
resource "aws_lb_target_group" "node_tg" {
  name        = "node-tg"
  port        = 3000
  protocol    = "HTTP"
  target_type = "instance"
  vpc_id      = aws_vpc.node_vpc.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "node-tg"
  }
}

# Listener: HTTP 80 -> target group
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.public_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.node_tg.arn
  }
}

output "alb_dns_name" {
  value = aws_lb.public_alb.dns_name
}