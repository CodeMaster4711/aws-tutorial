output "api_gateway_url" {
  description = "URL des API Gateway Endpoints"
  value       = "${aws_api_gateway_stage.api_stage.invoke_url}/log"
}

output "s3_bucket_name" {
  description = "Name des S3 Buckets"
  value       = aws_s3_bucket.logging_bucket.id
}

output "lambda_function_name" {
  description = "Name der Lambda Function"
  value       = aws_lambda_function.logging_function.function_name
}

output "lambda_function_arn" {
  description = "ARN der Lambda Function"
  value       = aws_lambda_function.logging_function.arn
}
