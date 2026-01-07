Document Outline: AgentCore Web Automation Deployment Guide

Section 1: Prerequisites
AWS Account with appropriate permissions
Python 3.10+ installed
Docker installed and running
AWS CLI configured with credentials
VS Code or Jupyter Notebook environment

Section 2: AWS IAM Setup
Create an IAM user with AdministratorAccess (or scoped permissions)
Generate access keys for programmatic access
Configure AWS CLI with credentials:
Section 3: S3 Bucket Setup
Create an S3 bucket for storing downloaded files
Bucket name: <client-name>-web-automation-storage
Region: us-east-1 (or preferred region)
Configure bucket policy (if needed)
Enable versioning (optional, recommended)
Section 4: AWS Systems Manager (SSM) Parameter Store
Store sensitive credentials (e.g., Nova Act API key):
Section 5: Amazon Cognito Setup
Create User Pool

Name: <client-name>-AgentCore-UserPool
Configure sign-in options (email, username, etc.)
Create Resource Server

Identifier: default-m2m-resource-server-<suffix>
Add custom scopes (e.g., read)
Create App Client

Name: <client-name>-AgentCore-AppClient
Enable client credentials flow
Add allowed scopes
Note down:
Client ID
Client Secret
Cognito Domain URL
Section 6: ECR Repository Setup
Create an ECR repository:
Note down the repository URI
Section 7: AgentCore Execution Role
Create IAM role for AgentCore Runtime
Attach policies:
AmazonBedrockFullAccess (or scoped Bedrock permissions)
S3 read/write for your bucket
SSM GetParameter for secrets
ECR pull permissions
Cognito permissions (if needed)
Example policy for S3:

Section 8: Agent Code Deployment
Clone or copy the agent code to local machine
Update configuration values:
S3 bucket name in agent code
SSM parameter name
Region
Install dependencies:
Run the Jupyter notebook first_stage_deployment.ipynb:
Execute the configure() cell with correct values
Execute the launch() cell to deploy
Section 9: Post-Deployment Configuration
Update Execution Role Permissions

Add S3 permissions for your bucket
Add SSM permissions for Nova Act API key
Add Cognito permissions (if needed)
Configure Inbound Auth (JWT/Cognito)

Go to AWS Console → Bedrock → AgentCore
Select your runtime
Configure Inbound Auth:
Protocol: HTTP
Auth Type: JWT
Discovery URL: https://cognito-idp.<region>.amazonaws.com/<user-pool-id>/.well-known/openid-configuration
Allowed Clients: <app-client-id>
Allowed Scopes: <resource-server>/<scope>
