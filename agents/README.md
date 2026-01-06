# Agents Directory

This directory contains the core implementation and deployment files for the AWS Bedrock AgentCore web automation agent.

## File Overview

### Agent Implementation

**`first_stage_agent.py`**

- The main agent code that handles web automation tasks
- Processes user requests and orchestrates the automation workflow
- Integrates with Amazon Bedrock Claude for AI reasoning
- Manages file downloads and S3 storage
- **Use case:** This is your agent logic

### Deployment & Configuration

**`agent_deployment.ipynb`**

- Notebook for deploying the agent to AWS Bedrock AgentCore
- Builds and uploads the Docker container image to ECR
- Creates the AgentCore runtime instance
- Configures authentication and permissions
- **Use case:** Run this to deploy your agent to AWS

**`.bedrock_agentcore.yaml`**

- Configuration file that defines your agent's runtime settings
- Specifies Docker image location, IAM role, and authentication
- Contains agent name, entrypoint, and AWS resource details
- **Use case:** Update this file with your AWS account information before deployment

**`Dockerfile`**

- Defines how to build the Docker container for your agent
- Specifies dependencies and runtime environment
- **Use case:** Used automatically during deployment; modify if you need different packages

**`.dockerignore`**

- Specifies which files to exclude from the Docker build
- Reduces container image size by ignoring unnecessary files
- **Use case:** Generally no changes needed

### Testing & Invocation

**`invoke_agent.ipynb`**

- Notebook for testing your deployed agent
- Gets authentication token from Cognito
- Sends requests to your running agent and displays responses
- **Use case:** Use this to test your agent after deployment

### Dependencies

**`requirements.txt`**

- Lists all Python packages needed to run the agent
- **Use case:** Update this if you add new Python libraries to your agent

**`pyproject.toml`**

- Project metadata and additional configuration
- **Use case:** Used by the uv package manager; generally no changes needed

### Optional Deployment Files

**`agent_runtime.ipynb`**

- Monitor and manage the running agent runtime
- Check logs and status

**`agent_gateway.ipynb`**

- Set up a gateway to expose multiple agents (advanced feature)
- Optional for production deployments

## Quick Start

1. **Update Configuration**

   ```
   Edit .bedrock_agentcore.yaml with your AWS account details
   ```

2. **Deploy Agent**

   ```
   Run: agent_deployment.ipynb
   ```

3. **Test Agent**
   ```
   Run: invoke_agent.ipynb
   ```

## Key Files to Modify

- `first_stage_agent.py` - Your agent logic
- `agent_deployment.ipynb` - Deployment settings (e.g., agent name, cognito details, S3 bucket, ecr uri)
- `requirements.txt` - Add Python dependencies here
- `.bedrock_agentcore.yaml` - AWS configuration (must update before deployment)
