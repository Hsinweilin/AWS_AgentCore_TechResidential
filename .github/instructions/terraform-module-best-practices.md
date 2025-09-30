# Terraform Module Best Practices

## 1. Use a Standard Structure
- Each module should have:
  - `main.tf` (resources)
  - `variables.tf` (inputs)
  - `outputs.tf` (outputs)
  - `README.md` (documentation)

## 2. Keep Modules Small and Focused
- Each module should do one thing (e.g., VPC, EC2, S3).
- Avoid mixing unrelated resources in a single module.

## 3. Use Meaningful Variable Names and Descriptions
- Always provide `description` for variables.
- Use clear, descriptive names.

## 4. Provide Sensible Defaults
- Set defaults for variables when possible, but allow overrides.

## 5. Use Outputs for Inter-Module Communication
- Output important resource IDs and attributes.
- Use outputs to connect modules in the root configuration.

## 6. Document Everything
- Include usage examples in `README.md`.
- List all inputs and outputs.

## 7. Avoid Hardcoding Values
- Use variables for all configurable values.
- Do not hardcode region, AMI IDs, etc.

## 8. Use Version Constraints
- Specify provider and module versions for stability.

## 9. Write Reusable and Composable Modules
- Design modules to be used in different environments/projects.

## 10. Test Your Modules
- Use `terraform validate` and `terraform plan`.
- Consider automated CI/CD for module changes.

---

**Example Module Structure:**
```
modules/
  aws_vpc/
    main.tf
    variables.tf
    outputs.tf
    README.md
```

**Example Usage:**
```hcl
module "vpc" {
  source = "./modules/aws_vpc"
  cidr_block = "10.0.0.0/16"
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  azs = ["us-east-1a", "us-east-1b"]
  tags = { Name = "MyVPC" }
}
```

---

For more, see the [Terraform Module Standards](https://www.terraform.io/docs/language/modules/index.html).
