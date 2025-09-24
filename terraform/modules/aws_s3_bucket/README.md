# AWS S3 Bucket Terraform Module

This module creates an AWS S3 bucket with configurable security, lifecycle, and notification settings.

## Features

- 🔒 **Security**: Configurable public access blocking, server-side encryption (AES256 or KMS)
- 📦 **Versioning**: Optional bucket versioning
- 🔄 **Lifecycle Management**: Configurable lifecycle rules for cost optimization
- 🌐 **CORS Support**: Cross-Origin Resource Sharing configuration
- 📢 **Notifications**: Lambda, SNS, and SQS notification support
- 🏷️ **Tagging**: Comprehensive resource tagging

## Usage

### Basic Usage

```hcl
module "s3_bucket" {
  source = "./modules/aws_s3_bucket"

  bucket_name = "my-application-bucket-${random_id.bucket_suffix.hex}"

  tags = {
    Environment = "dev"
    Project     = "web-automation"
  }
}
```

### Advanced Usage with Lifecycle Rules

```hcl
module "s3_bucket_with_lifecycle" {
  source = "./modules/aws_s3_bucket"

  bucket_name       = "my-storage-bucket-${random_id.bucket_suffix.hex}"
  enable_versioning = true
  force_destroy     = false

  lifecycle_rules = [
    {
      id     = "documents_lifecycle"
      status = "Enabled"
      filter = {
        prefix = "documents/"
      }
      transitions = [
        {
          days          = 30
          storage_class = "STANDARD_IA"
        },
        {
          days          = 90
          storage_class = "GLACIER"
        }
      ]
      expiration = {
        days = 365
      }
      noncurrent_version_expiration = {
        noncurrent_days = 90
      }
    },
    {
      id     = "temp_files_cleanup"
      status = "Enabled"
      filter = {
        prefix = "temp/"
      }
      expiration = {
        days = 7
      }
    }
  ]

  tags = {
    Environment = "prod"
    Project     = "web-automation"
  }
}
```

### Usage with KMS Encryption

```hcl
resource "aws_kms_key" "s3_key" {
  description = "KMS key for S3 bucket encryption"

  tags = {
    Name = "s3-encryption-key"
  }
}

resource "aws_kms_alias" "s3_key_alias" {
  name          = "alias/s3-bucket-key"
  target_key_id = aws_kms_key.s3_key.key_id
}

module "s3_bucket_encrypted" {
  source = "./modules/aws_s3_bucket"

  bucket_name       = "encrypted-bucket-${random_id.bucket_suffix.hex}"
  enable_versioning = true
  kms_key_id        = aws_kms_key.s3_key.arn

  tags = {
    Environment = "prod"
    Encrypted   = "true"
  }
}
```

### Usage with CORS Configuration

```hcl
module "s3_bucket_with_cors" {
  source = "./modules/aws_s3_bucket"

  bucket_name = "web-app-assets-${random_id.bucket_suffix.hex}"

  cors_rules = [
    {
      allowed_headers = ["*"]
      allowed_methods = ["GET", "POST", "PUT"]
      allowed_origins = ["https://myapp.example.com", "https://admin.example.com"]
      expose_headers  = ["ETag"]
      max_age_seconds = 3000
    }
  ]

  tags = {
    Environment = "prod"
    Purpose     = "web-assets"
  }
}
```

### Usage with Lambda Notifications

```hcl
resource "aws_lambda_function" "s3_processor" {
  filename         = "s3_processor.zip"
  function_name    = "s3-object-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
}

resource "aws_lambda_permission" "s3_invoke" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.s3_bucket_with_notifications.bucket_arn
}

module "s3_bucket_with_notifications" {
  source = "./modules/aws_s3_bucket"

  bucket_name = "processing-bucket-${random_id.bucket_suffix.hex}"

  lambda_notifications = [
    {
      lambda_function_arn = aws_lambda_function.s3_processor.arn
      events              = ["s3:ObjectCreated:*"]
      filter_prefix       = "uploads/"
      filter_suffix       = ".pdf"
    }
  ]

  tags = {
    Environment = "prod"
    Purpose     = "document-processing"
  }
}
```

## Input Variables

| Name                    | Description                                                                                            | Type           | Default | Required |
| ----------------------- | ------------------------------------------------------------------------------------------------------ | -------------- | ------- | :------: |
| bucket_name             | Name of the S3 bucket. Must be globally unique.                                                        | `string`       | n/a     |   yes    |
| force_destroy           | Boolean that indicates all objects should be deleted from the bucket when the bucket is destroyed      | `bool`         | `false` |    no    |
| tags                    | A map of tags to assign to the bucket                                                                  | `map(string)`  | `{}`    |    no    |
| enable_versioning       | Enable versioning for the S3 bucket                                                                    | `bool`         | `false` |    no    |
| kms_key_id              | The AWS KMS key ID to use for server-side encryption. If not provided, AES256 encryption will be used. | `string`       | `null`  |    no    |
| block_public_acls       | Whether Amazon S3 should block public ACLs for this bucket                                             | `bool`         | `true`  |    no    |
| block_public_policy     | Whether Amazon S3 should block public bucket policies for this bucket                                  | `bool`         | `true`  |    no    |
| ignore_public_acls      | Whether Amazon S3 should ignore public ACLs for this bucket                                            | `bool`         | `true`  |    no    |
| restrict_public_buckets | Whether Amazon S3 should restrict public bucket policies for this bucket                               | `bool`         | `true`  |    no    |
| lifecycle_rules         | List of lifecycle rules for the bucket                                                                 | `list(object)` | `[]`    |    no    |
| cors_rules              | List of CORS rules for the bucket                                                                      | `list(object)` | `[]`    |    no    |
| bucket_policy           | The bucket policy as a JSON document                                                                   | `string`       | `null`  |    no    |
| lambda_notifications    | List of Lambda function notifications for the bucket                                                   | `list(object)` | `[]`    |    no    |
| sns_notifications       | List of SNS topic notifications for the bucket                                                         | `list(object)` | `[]`    |    no    |
| sqs_notifications       | List of SQS queue notifications for the bucket                                                         | `list(object)` | `[]`    |    no    |

## Outputs

| Name                        | Description                                                                    |
| --------------------------- | ------------------------------------------------------------------------------ |
| bucket_id                   | The name of the bucket                                                         |
| bucket_arn                  | The ARN of the bucket                                                          |
| bucket_domain_name          | The bucket domain name                                                         |
| bucket_regional_domain_name | The bucket region-specific domain name                                         |
| bucket_hosted_zone_id       | The Route 53 Hosted Zone ID for this bucket's region                           |
| bucket_region               | The AWS region this bucket resides in                                          |
| bucket_website_endpoint     | The website endpoint, if the bucket is configured with a website               |
| bucket_website_domain       | The domain of the website endpoint, if the bucket is configured with a website |
| bucket_versioning_enabled   | Whether versioning is enabled for the bucket                                   |
| bucket_encryption_enabled   | Whether server-side encryption is enabled for the bucket                       |
| bucket_encryption_algorithm | The server-side encryption algorithm used                                      |
| kms_key_id                  | The KMS key ID used for encryption (if applicable)                             |

## Dependencies

This module requires:

- Terraform >= 1.5
- AWS Provider >= 5.0

## Security Considerations

- **Public Access**: By default, all public access is blocked. Modify the `block_public_*` variables only if you specifically need public access.
- **Encryption**: Server-side encryption is enabled by default with AES256. For enhanced security, provide a `kms_key_id`.
- **Versioning**: Enable versioning for important data to protect against accidental deletion or modification.
- **Lifecycle Rules**: Configure lifecycle rules to optimize storage costs and automatically clean up temporary files.

## Best Practices

1. **Naming**: Use descriptive, globally unique bucket names with appropriate prefixes/suffixes
2. **Tagging**: Always include environment, project, and ownership tags
3. **Encryption**: Use KMS keys for sensitive data
4. **Lifecycle**: Configure lifecycle rules to optimize costs
5. **Monitoring**: Set up appropriate notifications for important bucket events
6. **Access Control**: Use the principle of least privilege for bucket policies

## Examples

See the `examples/` directory for complete working examples of various use cases.

## Contributing

Please read the contributing guidelines before submitting changes to this module.

## License

This module is licensed under the MIT License. See LICENSE file for details.
