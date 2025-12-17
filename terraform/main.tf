terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket für Logs
resource "aws_s3_bucket" "logging_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = "Logging Bucket"
    Environment = var.environment
  }
}

# IAM Rolle für Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-role"
  }
}

# IAM Policy für S3 Zugriff
resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "${var.project_name}-s3-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.logging_bucket.arn}/*"
      }
    ]
  })
}

# Lambda Code als ZIP packen
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../function/lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda Function
resource "aws_lambda_function" "logging_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.lambda_function_name
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.12"
  timeout         = 30

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.logging_bucket.id
    }
  }

  tags = {
    Name = var.lambda_function_name
  }
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "logging_api" {
  name        = "${var.project_name}-api"
  description = "API Gateway für Logging System"
}

# API Gateway Resource (/log)
resource "aws_api_gateway_resource" "log_resource" {
  rest_api_id = aws_api_gateway_rest_api.logging_api.id
  parent_id   = aws_api_gateway_rest_api.logging_api.root_resource_id
  path_part   = "log"
}

# API Gateway Method (POST)
resource "aws_api_gateway_method" "log_post" {
  rest_api_id   = aws_api_gateway_rest_api.logging_api.id
  resource_id   = aws_api_gateway_resource.log_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration mit Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.logging_api.id
  resource_id             = aws_api_gateway_resource.log_resource.id
  http_method             = aws_api_gateway_method.log_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.logging_function.invoke_arn
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.logging_api.id

  depends_on = [
    aws_api_gateway_integration.lambda_integration
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.logging_api.id
  stage_name    = var.api_stage_name
}

# Lambda Permission für API Gateway
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.logging_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.logging_api.execution_arn}/*/*"
}
