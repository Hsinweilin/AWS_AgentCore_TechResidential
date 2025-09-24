# Quick Start Guide

This guide will help you set up the AWS Bedrock Agent Web Automation System for development and testing.

## Prerequisites

Before you begin, ensure you have the following:

- AWS Account with access to AWS Bedrock
- AWS CLI installed and configured
- Terraform CLI (v1.0.0+)
- Node.js (v14.0.0+)
- Git

## Step 1: Clone the Repository

```bash
git clone https://github.com/Hsinweilin/AWS_AgentCore_TechResidential.git
cd AWS_AgentCore_TechResidential
```

## Step 2: Configure AWS Credentials

Ensure your AWS credentials are configured with appropriate permissions:

```bash
aws configure
```

You'll need permissions for the following services:

- Amazon Bedrock
- Lambda
- S3
- SSM Parameter Store
- EventBridge
- SES
- IAM (for setup)

## Step 3: Set Up Infrastructure

Navigate to the infrastructure directory and initialize Terraform:

```bash
cd infrastructure
terraform init
```

Create a `terraform.tfvars` file with your specific variables:

```hcl
aws_region       = "us-east-1"  # Change to your preferred region
project_name     = "bedrock-web-automation"
environment      = "dev"
aws_account_id   = "123456789012"  # Replace with your AWS account ID
deployment_bucket = "my-deployment-bucket"  # Replace with your deployment bucket
sender_email     = "notifications@example.com"  # Replace with your verified email
```

Deploy the infrastructure:

```bash
terraform apply
```

## Step 4: Configure Bedrock Agent

1. Follow the instructions in `samples/bedrock_agent_configuration.md` to set up your Bedrock agent
2. Note down the agent ID and agent alias ID
3. Update the deployed Lambda function with these values:

```bash
aws lambda update-function-configuration \
  --function-name bedrock-web-automation-agent-trigger-dev \
  --environment "Variables={BEDROCK_AGENT_ID=your-agent-id,BEDROCK_AGENT_ALIAS_ID=your-agent-alias-id}"
```

## Step 5: Deploy Lambda Functions

Build and deploy the Lambda functions:

```bash
cd ../src/lambda
npm install
npm run build
npm run deploy
```

## Step 6: Test Basic Functionality

Create a test prompt file:

```bash
aws s3 cp samples/sample_prompt.txt s3://bedrock-web-automation-prompt-files-dev/test/prompt.txt
```

Store test credentials in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name "/bedrock-web-automation/test/credentials" \
  --secret-string '{"username":"test-user","password":"test-password"}'
```

Store test URL in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name "/bedrock-web-automation/test/url" \
  --secret-string '{"url":"https://example.com/login"}'
```

Invoke the Lambda function manually to test:

```bash
aws lambda invoke \
  --function-name bedrock-web-automation-agent-trigger-dev \
  --payload '{"taskId":"test-task","userId":"test-user","urlSecretName":"/bedrock-web-automation/test/url","credentialsSecretName":"/bedrock-web-automation/test/credentials","promptFileKey":"test/prompt.txt","outputBucket":"bedrock-web-automation-documents-dev","notificationEmail":"your-email@example.com"}' \
  response.json
```

Check the CloudWatch logs for execution details:

```bash
aws logs get-log-events \
  --log-group-name "/aws/lambda/bedrock-web-automation-agent-trigger-dev" \
  --log-stream-name $(aws logs describe-log-streams --log-group-name "/aws/lambda/bedrock-web-automation-agent-trigger-dev" --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text)
```

## Step 7: Set Up UI (Optional)

If you want to set up the user interface:

```bash
cd ../ui/web
npm install
npm run dev
```

The development server will start, and you can access the UI at http://localhost:3000.

## Step 8: Configure Schedule

Create a test schedule using EventBridge:

```bash
aws events put-rule \
  --name "bedrock-web-automation-test-schedule" \
  --schedule-expression "rate(1 day)" \
  --state "DISABLED"  # Disabled for testing

aws events put-targets \
  --rule "bedrock-web-automation-test-schedule" \
  --targets '[{"Id":"1","Arn":"arn:aws:lambda:us-east-1:123456789012:function:bedrock-web-automation-agent-trigger-dev","Input":"{\"taskId\":\"test-task\",\"userId\":\"test-user\",\"urlSecretName\":\"/bedrock-web-automation/test/url\",\"credentialsSecretName\":\"/bedrock-web-automation/test/credentials\",\"promptFileKey\":\"test/prompt.txt\",\"outputBucket\":\"bedrock-web-automation-documents-dev\",\"notificationEmail\":\"your-email@example.com\"}"}]'
```

## Next Steps

- Review the complete documentation in the `docs` directory
- Explore the sample code in the `samples` directory
- Check out the implementation roadmap in `samples/implementation_roadmap.md`
- Start developing additional features based on the project structure

## Troubleshooting

### Common Issues

1. **Lambda Function Timeout**

   - Increase the Lambda timeout value in the Terraform configuration
   - Optimize the Lambda code for performance

2. **Bedrock Agent Permissions**

   - Ensure the agent has the necessary permissions for browser interactions
   - Check the agent execution logs for specific errors

3. **Secrets Manager Access**

   - Verify the Lambda execution role has permission to access Secrets Manager
   - Check the secret name and path for typos
   - Ensure the secret exists in the specified region

4. **S3 Access Issues**
   - Confirm bucket policies allow the Lambda function to read/write objects
   - Check for object key typos in the function parameters

For more detailed troubleshooting, refer to the documentation or check the CloudWatch logs for specific error messages.
