# Terraform version constraints and provider configurations

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.10.0"
    }
  }
  cloud { 
    organization = "TechResidential" 
    workspaces { 
      name = "Techresidential" 
    } 
  } 
}
