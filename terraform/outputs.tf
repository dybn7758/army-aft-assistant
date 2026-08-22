output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value = [
    aws_subnet.public_1.id,
    aws_subnet.public_2.id,
  ]
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value = [
    aws_subnet.private_1.id,
    aws_subnet.private_2.id,
  ]
}

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "ECS security group ID"
  value       = aws_security_group.ecs.id
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.postgres.db_name
}

output "rds_secret_arn" {
  description = "Secrets Manager ARN containing RDS credentials"
  value = (
    aws_db_instance.postgres.master_user_secret[0].secret_arn
  )
  sensitive = true
}

output "backend_ecr_repository_url" {
  description = "ECR repository URL for the Flask backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "backend_ecr_repository_name" {
  description = "ECR repository name"
  value       = aws_ecr_repository.backend.name
}

output "backend_load_balancer_url" {
  description = "Public URL for Flask backend"
  value       = "http://${aws_lb.backend.dns_name}"
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "mem0_secret_arn" {
  description = "Secrets Manager ARN for Mem0"
  value       = aws_secretsmanager_secret.mem0.arn
}

output "frontend_bucket_name" {
  description = "S3 bucket containing the React frontend"
  value       = aws_s3_bucket.frontend.id
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.frontend.id
}

output "frontend_url" {
  description = "CloudFront URL for the AFT Assistant"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}