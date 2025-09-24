# AWS_AgentCore_TechResidential

This repo is for the development of a web automation system using AWS Bedrock AgentCore with browser tools.

## Overview

This project implements a cloud-based AI agent using AWS Bedrock AgentCore to automate browser interactions such as website logins and document downloads. The system allows users to schedule automated tasks, securely store credentials, and receive email notifications with downloaded documents.

## Key Features

- **Browser Automation**: Automatically log in to websites and download documents using AWS Bedrock browser tools
- **Secure Credential Management**: Store user credentials securely in AWS Secrets Manager
- **Custom Browser Instructions**: Use customizable prompt files stored in S3 to guide browser automation
- **Flexible Scheduling**: Configure one-time or recurring tasks using Amazon EventBridge
- **Document Storage**: Save downloaded documents to Amazon S3
- **Email Notifications**: Send email notifications with document copies to users

## Architecture

The system uses a serverless architecture built on AWS services:

- **AWS Bedrock**: Provides the AI agent and browser automation capabilities
- **AWS Lambda**: Handles the execution of the agent and notification logic
- **Amazon S3**: Stores prompt files and downloaded documents
- **AWS Secrets Manager**: Securely stores credentials
- **Amazon EventBridge**: Schedules agent execution
- **Amazon SES**: Sends email notifications

## Project Documentation

- [SPECIFICATION.md](SPECIFICATION.md) - Detailed system requirements and specifications
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project organization and implementation approach

## Getting Started

See the Project Structure document for detailed implementation steps and development approach.
