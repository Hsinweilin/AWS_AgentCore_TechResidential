---
mode: agent
tools: ["codebase"]
---

# Create New Terraform Modules in "modules/" Directory

## What This Prompt Does

When you specify a terraform module name, I will generate module folder structure following best practices

## Best Practices To Follow

For detailed best practices, see [terraform-module-best-practices.md](../instructions/terraform-module-best-practices.md).

## How to Use This Prompt

The user will call this prompt and specify the module name, for example: "aws_ec2"
Check if the module already exists in the "modules/" directory. If it does, respond with "Module already exists."
If not, follow the steps to create the module structure.

## Steps

### 1. Create Module Directory

- Each module should have:
  - `main.tf` (resources)
  - `variables.tf` (inputs)
  - `outputs.tf` (outputs)
  - `README.md` (documentation)

### 2. Define module in main.tf

- Define the necessary AWS resources for the module.

### 3. Define Input Variables in variables.tf

- Always provide `description` for variables and use clear, descriptive names.
- Set defaults for variables when possible, but allow overrides.

### 4. Define Output Values in outputs.tf

- Use outputs to expose important information about the module's resources.
- Include `description` for each output.

### 5. Document the Module in README.md

- Provide an overview of the module's purpose and functionality.
- Include usage examples, including input variables and expected outputs.
- Document any dependencies or prerequisites for using the module.
