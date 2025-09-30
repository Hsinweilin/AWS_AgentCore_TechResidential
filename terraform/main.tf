# Main Terraform configuration for AWS Bedrock Agent Web Automation System

locals {
  name_prefix   = "${var.project_name}-${var.environment}"
}
# S3 bucket for storing prompt files and downloaded documents
# Using single bucket with prefix-based organization (recommended approach)
module "web_automation_storage" {
  source = "./modules/aws_s3_bucket"

  bucket_name       = "${local.name_prefix}-storage"
  enable_versioning = true
  force_destroy     = var.environment == "dev" ? true : false

  # only backend resources are accessing s3, so no CORS needed
}

# # IAM role for Lambda functions
# resource "aws_iam_role" "lambda_role" {
#   name = "${var.project_name}-lambda-role-${var.environment}"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "sts:AssumeRole"
#         Effect = "Allow"
#         Principal = {
#           Service = "lambda.amazonaws.com"
#         }
#       }
#     ]
#   })
# }

# # IAM policy for Lambda functions
# resource "aws_iam_policy" "lambda_policy" {
#   name        = "${var.project_name}-lambda-policy-${var.environment}"
#   description = "Policy for Lambda functions in the ${var.project_name} project"

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "logs:CreateLogGroup",
#           "logs:CreateLogStream",
#           "logs:PutLogEvents"
#         ]
#         Effect   = "Allow"
#         Resource = "arn:aws:logs:*:*:*"
#       },
#       {
#         Action = [
#           "s3:GetObject",
#           "s3:PutObject",
#           "s3:ListBucket"
#         ]
#         Effect = "Allow"
#         Resource = [
#           aws_s3_bucket.prompt_bucket.arn,
#           "${aws_s3_bucket.prompt_bucket.arn}/*",
#           aws_s3_bucket.document_bucket.arn,
#           "${aws_s3_bucket.document_bucket.arn}/*"
#         ]
#       },
#       {
#         Action = [
#           "secretsmanager:GetSecretValue",
#           "secretsmanager:DescribeSecret"
#         ]
#         Effect   = "Allow"
#         Resource = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:/${var.project_name}/*"
#       },
#       {
#         Action = [
#           "bedrock:InvokeAgent"
#         ]
#         Effect   = "Allow"
#         Resource = "*"
#       },
#       {
#         Action = [
#           "ses:SendEmail",
#           "ses:SendRawEmail"
#         ]
#         Effect   = "Allow"
#         Resource = "*"
#       }
#     ]
#   })
# }

# # Attach policy to role
# resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
#   role       = aws_iam_role.lambda_role.name
#   policy_arn = aws_iam_policy.lambda_policy.arn
# }

# # Lambda function for agent trigger
# resource "aws_lambda_function" "agent_trigger" {
#   function_name = "${var.project_name}-agent-trigger-${var.environment}"
#   role          = aws_iam_role.lambda_role.arn
#   handler       = "agent_trigger.handler"
#   runtime       = "nodejs18.x"
#   timeout       = 300 # 5 minutes
#   memory_size   = 256

#   s3_bucket = var.deployment_bucket
#   s3_key    = "${var.project_name}/${var.environment}/agent_trigger.zip"

#   environment {
#     variables = {
#       PROMPT_BUCKET          = aws_s3_bucket.prompt_bucket.id
#       BEDROCK_AGENT_ID       = var.bedrock_agent_id
#       BEDROCK_AGENT_ALIAS_ID = var.bedrock_agent_alias_id
#       SENDER_EMAIL           = var.sender_email
#     }
#   }
# }

# # EventBridge role
# resource "aws_iam_role" "eventbridge_role" {
#   name = "${var.project_name}-eventbridge-role-${var.environment}"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "sts:AssumeRole"
#         Effect = "Allow"
#         Principal = {
#           Service = "events.amazonaws.com"
#         }
#       }
#     ]
#   })
# }

# # EventBridge policy
# resource "aws_iam_policy" "eventbridge_policy" {
#   name        = "${var.project_name}-eventbridge-policy-${var.environment}"
#   description = "Policy for EventBridge in the ${var.project_name} project"

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action   = "lambda:InvokeFunction"
#         Effect   = "Allow"
#         Resource = aws_lambda_function.agent_trigger.arn
#       }
#     ]
#   })
# }

# # Attach policy to role
# resource "aws_iam_role_policy_attachment" "eventbridge_policy_attachment" {
#   role       = aws_iam_role.eventbridge_role.name
#   policy_arn = aws_iam_policy.eventbridge_policy.arn
# }

# # Example EventBridge rule for scheduled trigger
# resource "aws_cloudwatch_event_rule" "scheduled_trigger" {
#   name                = "${var.project_name}-scheduled-trigger-${var.environment}"
#   description         = "Scheduled trigger for browser automation agent"
#   schedule_expression = "cron(0 8 ? * MON-FRI *)" # Example: Every weekday at 8:00 AM
# }

# # EventBridge target
# resource "aws_cloudwatch_event_target" "lambda_target" {
#   rule      = aws_cloudwatch_event_rule.scheduled_trigger.name
#   target_id = "InvokeLambda"
#   arn       = aws_lambda_function.agent_trigger.arn
#   role_arn  = aws_iam_role.eventbridge_role.arn

#   # Example input for the Lambda function
#   input = jsonencode({
#     taskId                   = "example-task"
#     userId                   = "example-user"
#     urlParameterName         = "/${var.project_name}/example-task/url"
#     credentialsParameterName = "/${var.project_name}/example-task/credentials"
#     promptFileKey            = "example-user/example-task/prompt.txt"
#     outputBucket             = aws_s3_bucket.document_bucket.id
#     notificationEmail        = "user@example.com"
#   })
# }

# # CloudWatch Log Group for Lambda
# resource "aws_cloudwatch_log_group" "agent_trigger_logs" {
#   name              = "/aws/lambda/${aws_lambda_function.agent_trigger.function_name}"
#   retention_in_days = 14
# }

# # Outputs
# output "prompt_bucket_name" {
#   value       = aws_s3_bucket.prompt_bucket.id
#   description = "Name of the S3 bucket for storing prompt files"
# }

# output "document_bucket_name" {
#   value       = aws_s3_bucket.document_bucket.id
#   description = "Name of the S3 bucket for storing downloaded documents"
# }

# output "lambda_function_name" {
#   value       = aws_lambda_function.agent_trigger.function_name
#   description = "Name of the Lambda function for triggering the agent"
# }

# output "eventbridge_rule_name" {
#   value       = aws_cloudwatch_event_rule.scheduled_trigger.name
#   description = "Name of the EventBridge rule for scheduled triggers"
# }
