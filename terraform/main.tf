# --------------------------------------------------
# Availability Zones
# --------------------------------------------------

data "aws_availability_zones" "available" {
  state = "available"
}


# --------------------------------------------------
# VPC
# --------------------------------------------------

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name    = "${var.project_name}-vpc"
    Project = var.project_name
  }
}


# --------------------------------------------------
# Internet Gateway
# --------------------------------------------------

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "${var.project_name}-igw"
    Project = var.project_name
  }
}


# --------------------------------------------------
# Public Subnets
#
# ALB and ECS will initially run here.
# --------------------------------------------------

resource "aws_subnet" "public_1" {
  vpc_id = aws_vpc.main.id

  cidr_block = "10.0.1.0/24"

  availability_zone = data.aws_availability_zones.available.names[0]

  map_public_ip_on_launch = true

  tags = {
    Name    = "${var.project_name}-public-1"
    Project = var.project_name
  }
}


resource "aws_subnet" "public_2" {
  vpc_id = aws_vpc.main.id

  cidr_block = "10.0.2.0/24"

  availability_zone = data.aws_availability_zones.available.names[1]

  map_public_ip_on_launch = true

  tags = {
    Name    = "${var.project_name}-public-2"
    Project = var.project_name
  }
}


# --------------------------------------------------
# Private Subnets
#
# RDS PostgreSQL will run here.
# --------------------------------------------------

resource "aws_subnet" "private_1" {
  vpc_id = aws_vpc.main.id

  cidr_block = "10.0.11.0/24"

  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name    = "${var.project_name}-private-1"
    Project = var.project_name
  }
}


resource "aws_subnet" "private_2" {
  vpc_id = aws_vpc.main.id

  cidr_block = "10.0.12.0/24"

  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name    = "${var.project_name}-private-2"
    Project = var.project_name
  }
}


# --------------------------------------------------
# Public Route Table
# --------------------------------------------------

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name    = "${var.project_name}-public-rt"
    Project = var.project_name
  }
}


# --------------------------------------------------
# Public Route Table Associations
# --------------------------------------------------

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}


resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}


# --------------------------------------------------
# ALB Security Group
#
# Internet -> ALB
# --------------------------------------------------

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Allow HTTP traffic to the application load balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-alb-sg"
    Project = var.project_name
  }
}


# --------------------------------------------------
# ECS Security Group
#
# ALB -> Flask backend
# --------------------------------------------------

resource "aws_security_group" "ecs" {
  name        = "${var.project_name}-ecs-sg"
  description = "Allow traffic from ALB to Flask backend"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Flask from ALB"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-ecs-sg"
    Project = var.project_name
  }
}


# --------------------------------------------------
# RDS Security Group
#
# ECS -> PostgreSQL only
# --------------------------------------------------

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow PostgreSQL access from ECS only"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  tags = {
    Name    = "${var.project_name}-rds-sg"
    Project = var.project_name
  }
}

# --------------------------------------------------
# RDS Subnet Group
#
# PostgreSQL stays in private subnets.
# --------------------------------------------------

resource "aws_db_subnet_group" "main" {
  name = "${var.project_name}-db-subnet-group"

  subnet_ids = [
    aws_subnet.private_1.id,
    aws_subnet.private_2.id,
  ]

  tags = {
    Name    = "${var.project_name}-db-subnet-group"
    Project = var.project_name
  }
}

# --------------------------------------------------
# RDS PostgreSQL
# --------------------------------------------------

resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-postgres"

  engine = "postgres"

  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = 50
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username

  # AWS generates the password and stores it
  # in Secrets Manager.
  manage_master_user_password = true

  db_subnet_group_name = aws_db_subnet_group.main.name

  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false
  multi_az            = false

  backup_retention_period = 1

  deletion_protection = false

  skip_final_snapshot = true

  tags = {
    Name    = "${var.project_name}-postgres"
    Project = var.project_name
  }
}

# --------------------------------------------------
# ECR Repository
# --------------------------------------------------

resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name    = "${var.project_name}-backend"
    Project = var.project_name
  }
}

resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"

        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }

        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_repository" "frontend" {
  name                 = "${var.project_name}-frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name    = "${var.project_name}-frontend"
    Project = var.project_name
  }
}

# --------------------------------------------------
# Mem0 Secret
#
# Terraform creates the secret container only.
# We will add the actual API key separately so the
# key does not appear in Terraform source code.
# --------------------------------------------------

resource "aws_secretsmanager_secret" "mem0" {
  name = "${var.project_name}/mem0-api-key"

  tags = {
    Project = var.project_name
  }
}


# --------------------------------------------------
# ECS Task Execution Role
#
# Used by ECS itself to:
# - pull images from ECR
# - write logs
# - retrieve injected secrets
# --------------------------------------------------

resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role = aws_iam_role.ecs_execution.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${var.project_name}-execution-secrets"

  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "secretsmanager:GetSecretValue"
        ]

        Resource = [
          aws_db_instance.postgres.master_user_secret[0].secret_arn,
          aws_secretsmanager_secret.mem0.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_role_policy" "bedrock" {
  name = "${var.project_name}-bedrock-policy"

  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]

        Resource = "*"
      }
    ]
  })
}


resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}-backend"
  retention_in_days = 7

  tags = {
    Project = var.project_name
  }
}


resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  tags = {
    Project = var.project_name
  }
}

resource "aws_lb" "backend" {
  name               = "aft-assistant-alb"
  internal           = false
  load_balancer_type = "application"

  security_groups = [
    aws_security_group.alb.id
  ]

  subnets = [
    aws_subnet.public_1.id,
    aws_subnet.public_2.id,
  ]

  tags = {
    Project = var.project_name
  }
}


resource "aws_lb_target_group" "backend" {
  name        = "aft-backend-tg"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/api/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Project = var.project_name
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.backend.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}


resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = "512"
  memory = "1024"

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name = "backend"

      image = "${aws_ecr_repository.backend.repository_url}:latest"

      essential = true

      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "DB_HOST"
          value = aws_db_instance.postgres.address
        },
        {
          name  = "DB_PORT"
          value = tostring(aws_db_instance.postgres.port)
        },
        {
          name  = "DB_NAME"
          value = var.db_name
        },
        {
          name  = "DB_USER"
          value = var.db_username
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        }
      ]

      secrets = [
        {
          name = "DB_PASSWORD"

          valueFrom = "${aws_db_instance.postgres.master_user_secret[0].secret_arn}:password::"
        },
        {
          name      = "MEM0_API_KEY"
          valueFrom = aws_secretsmanager_secret.mem0.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "backend"
        }
      }
    }
  ])

  tags = {
    Project = var.project_name
  }
}


resource "aws_ecs_service" "backend" {
  name    = "${var.project_name}-backend"
  cluster = aws_ecs_cluster.main.id

  task_definition = aws_ecs_task_definition.backend.arn

  desired_count = 1
  launch_type   = "FARGATE"

  network_configuration {
    subnets = [
      aws_subnet.public_1.id,
      aws_subnet.public_2.id,
    ]

    security_groups = [
      aws_security_group.ecs.id
    ]

    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 5000
  }

  depends_on = [
    aws_lb_listener.http
  ]

  tags = {
    Project = var.project_name
  }
}


# --------------------------------------------------
# Frontend S3 Bucket
# --------------------------------------------------

resource "aws_s3_bucket" "frontend" {
  bucket_prefix = "army-aft-assistant-frontend-"

  tags = {
    Name    = "${var.project_name}-frontend"
    Project = var.project_name
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# --------------------------------------------------
# CloudFront Origin Access Control
# --------------------------------------------------

resource "aws_cloudfront_origin_access_control" "frontend" {
  name = "${var.project_name}-frontend-oac"

  description                       = "OAC for AFT frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}


# --------------------------------------------------
# CloudFront Distribution
# --------------------------------------------------

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "frontend-s3"

    origin_access_control_id = (
      aws_cloudfront_origin_access_control.frontend.id
    )
  }

  origin {
    domain_name = aws_lb.backend.dns_name
    origin_id   = "backend-alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id = "frontend-s3"

    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = [
      "GET",
      "HEAD",
      "OPTIONS"
    ]

    cached_methods = [
      "GET",
      "HEAD"
    ]

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  ordered_cache_behavior {
    path_pattern     = "/api/*"
    target_origin_id = "backend-alb"

    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = [
      "GET",
      "HEAD",
      "OPTIONS",
      "POST",
      "PUT",
      "PATCH",
      "DELETE"
    ]

    cached_methods = [
      "GET",
      "HEAD"
    ]

    cache_policy_id = data.aws_cloudfront_cache_policy.caching_disabled.id

    origin_request_policy_id = (
      data.aws_cloudfront_origin_request_policy.all_viewer.id
    )
  }

  # # React SPA routing
  # custom_error_response {
  #   error_code         = 403
  #   response_code      = 200
  #   response_page_path = "/index.html"
  # }

  # custom_error_response {
  #   error_code         = 404
  #   response_code      = 200
  #   response_page_path = "/index.html"
  # }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Project = var.project_name
  }
}


# --------------------------------------------------
# Allow CloudFront to read S3
# --------------------------------------------------

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "AllowCloudFront"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }

        Action = "s3:GetObject"

        Resource = "${aws_s3_bucket.frontend.arn}/*"

        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
          }
        }
      }
    ]
  })
}

data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_origin_request_policy" "all_viewer" {
  name = "Managed-AllViewer"
}



