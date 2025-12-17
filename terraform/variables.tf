variable "aws_region" {
  description = "AWS Region für das Deployment"
  type        = string
  default     = "eu-central-1"
}

variable "bucket_name" {
  description = "Name des S3 Buckets für Logs (muss global eindeutig sein)"
  type        = string
}

variable "project_name" {
  description = "Name des Projekts (wird für Ressourcen-Namen verwendet)"
  type        = string
  default     = "logging-system"
}

variable "environment" {
  description = "Umgebung (dev, prod, etc.)"
  type        = string
  default     = "dev"
}

variable "lambda_function_name" {
  description = "Name der Lambda Function"
  type        = string
  default     = "TrafficLoggingFunction"
}

variable "api_stage_name" {
  description = "Name des API Gateway Stages"
  type        = string
  default     = "prod"
}
