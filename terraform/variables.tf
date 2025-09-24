# Variables for AWS Bedrock Agent Web Automation System

# Core Configuration
variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "AWS region must be a valid AWS region format (e.g., us-east-1)."
  }
}

variable "project_name" {
  description = "The name of the project, used as a prefix for resource names"
  type        = string
  default     = "bedrock-web-automation"
}

variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

# Bedrock Configuration
variable "bedrock_model_id" {
  description = "The Bedrock foundation model ID to use"
  type        = string
  default     = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
}

# Storage Configuration
variable "s3_lifecycle_transition_days" {
  description = "Number of days before transitioning S3 objects to IA storage"
  type        = number
  default     = 30
}

variable "s3_lifecycle_expiration_days" {
  description = "Number of days before S3 objects expire"
  type        = number
  default     = 365
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Name of the application database"
  type        = string
  default     = "webautomation"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "admin"
}

# Web Application Configuration
variable "web_app_port" {
  description = "Port for the web application"
  type        = number
  default     = 3000
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "ecs_cpu" {
  description = "CPU units for ECS tasks"
  type        = number
  default     = 256
}

variable "ecs_memory" {
  description = "Memory for ECS tasks"
  type        = number
  default     = 512
}

# Example scheduler configuration
variable "schedule_expression" {
  description = "The schedule expression for the EventBridge rule"
  type        = string
  default     = "cron(0 8 ? * MON-FRI *)" # Every weekday at 8:00 AM
}

variable "lambda_timeout" {
  description = "The timeout for the Lambda function in seconds"
  type        = number
  default     = 300 # 5 minutes
}

variable "lambda_memory_size" {
  description = "The memory size for the Lambda function in MB"
  type        = number
  default     = 256
}

variable "log_retention_days" {
  description = "The number of days to retain CloudWatch logs"
  type        = number
  default     = 14
}
