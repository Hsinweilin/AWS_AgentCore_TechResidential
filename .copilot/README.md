# AWS Copilot Configuration

This folder contains the AWS Copilot configuration for the AWS AgentCore TechResidential application.

## Structure

- `copilot.yml` - Main application configuration
- `environments/` - Environment-specific configurations
  - `development/` - Development environment configuration
- `services/` - Service configurations
  - `agentcore/` - Main AgentCore service configuration
- `pipelines/` - CI/CD pipeline configurations

## Usage

To deploy using AWS Copilot CLI:

```bash
# Initialize copilot application
copilot app init aws-agentcore-techresidential

# Deploy an environment
copilot env deploy --name development

# Deploy a service
copilot svc deploy --name agentcore --env development
```

## Prerequisites

- AWS CLI configured with appropriate permissions
- AWS Copilot CLI installed
- Docker installed for container builds

## Environment Variables

The service configuration references the following secrets that should be configured in AWS Systems Manager Parameter Store or AWS Secrets Manager:

- `DATABASE_URL` - Database connection string
- `API_KEY` - API authentication key

## More Information

For more details about AWS Copilot, visit: https://aws.github.io/copilot-cli/