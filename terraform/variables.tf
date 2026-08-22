variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Local AWS CLI profile"
  type        = string
  default     = "Ying"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "army-aft-assistant"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "aft_assistant"
}

variable "db_username" {
  description = "PostgreSQL database username"
  type        = string
  default     = "aft_user"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS storage in GB"
  type        = number
  default     = 20
}

