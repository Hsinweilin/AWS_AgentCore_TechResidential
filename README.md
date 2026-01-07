# AWS_AgentCore_TechResidential

This repo is for the development of a web automation system using AWS Bedrock AgentCore with browser tools. Some of the source code is adapted from the open source official [AWS Bedrock AgentCore repositories](https://github.com/awslabs/amazon-bedrock-agentcore-samples)

## Overview

This project implements a cloud-based AI agent using AWS Bedrock AgentCore to automate browser interactions such as website logins and document downloads. The system allows users to schedule automated tasks, securely store credentials, and receive s3 pre-signed URLs for downloaded documents.

## Architecture

The system uses a serverless architecture built on AWS services:

- **AWS Bedrock AgentCore**: Orchestrates the AI agent runtime/Identity/Gateway and manages browser automation workflows
- **Amazon Bedrock Models**: Provides Claude for AI reasoning and task planning
- **AWS Cognito User Pool**: Manages authentication and authorization for agent invocations
- **Amazon ECR**: Stores the containerized agent image for deployment
- **AWS Lambda**: Optional serverless function serve as MCP tools 
- **Amazon S3**: Stores prompt files and downloaded documents
- **AWS Systems Manager Parameter Store**: Stores configuration parameters and sensitive credentials
- **AWS Secrets Manager**: Securely stores and rotates sensitive credentials

## Getting Started

### 1. Prerequisites

Before you begin, ensure you have the following:

- **AWS Account** with an IAM user with AdministratorAccess
  - Setup Guide: Follow [this tutorial](https://www.youtube.com/watch?v=A_CAT3_1s5E) to create an IAM user
  - Note: AdministratorAccess is used for development simplicity. For production, use least-privilege IAM roles
- **AWS CLI** installed and configured
  - Installation Guide: [AWS CLI Getting Started](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  - Configuration Guide: [AWS CLI Configure](https://docs.aws.amazon.com/cli/latest/reference/configure/)
  - Quick setup:
    ```bash
    aws configure
    ```
    Then provide your AWS Access Key ID and Secret Access Key when prompted
- **Python 3.10+** installed
- **Jupyter Notebook** installed
  - Installation Guide: [Jupyter Installation](https://jupyter.org/install)
  - Quick setup:
    ```bash
    pip install jupyterlab
    ```
- **uv** (fast Python package manager) installed
  - Quick setup:
    ```bash
    pip install uv
    ```
- **Docker** installed and running
  - Installation Guide: [Docker Install](https://docs.docker.com/engine/install/#get-started)
  - Verify installation: `docker --version`

### 2. Start Jupyter Notebook

To start Jupyter Lab with the project environment, run the following commands:

```bash
# Initialize the project with uv (only needed if first time)
uv init

# Start Jupyter Lab with the active virtual environment
uv run --active --with jupyter jupyter lab
```

### 3. Configure AWS Resources

Follow the steps in [docs/configure_aws_resources.md](docs/configure_aws_resources.md) to set up necessary AWS resources like S3 bucket, Cognito, Parameter Store, Agentcore Execution Role, and ECR Repository.

### 4. Exectuting agent_deployment.ipynb

Open and run the `agent_deployment.ipynb` notebook in Jupyter Lab to deploy your agent. This notebook will guide you through configuring and deploying your agent to AWS Bedrock AgentCore. Remember to update the notebook with your specific AWS resource names and configurations before running it, including test client data (your website, username, password, client name, and prompt file). Test the agent locally first to ensure it works as expected before deploying.

### 5. Invoke Agent with invoke_agent.ipynb

Use the `invoke_agent.ipynb` notebook to test your deployed agent. Update the notebook with your Cognito details and Agent ARN before running it. This notebook will help you get an authentication token and send requests to your running agent, displaying the responses.
