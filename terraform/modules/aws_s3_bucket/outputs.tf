# Output Values for AWS S3 Bucket Module

output "bucket_id" {
  description = "The name of the bucket"
  value       = aws_s3_bucket.this.id
}

output "bucket_arn" {
  description = "The ARN of the bucket"
  value       = aws_s3_bucket.this.arn
}

output "bucket_domain_name" {
  description = "The bucket domain name"
  value       = aws_s3_bucket.this.bucket_domain_name
}

output "bucket_regional_domain_name" {
  description = "The bucket region-specific domain name"
  value       = aws_s3_bucket.this.bucket_regional_domain_name
}

output "bucket_hosted_zone_id" {
  description = "The Route 53 Hosted Zone ID for this bucket's region"
  value       = aws_s3_bucket.this.hosted_zone_id
}

output "bucket_region" {
  description = "The AWS region this bucket resides in"
  value       = aws_s3_bucket.this.region
}

output "bucket_versioning_enabled" {
  description = "Whether versioning is enabled for the bucket"
  value       = var.enable_versioning
}

output "bucket_encryption_enabled" {
  description = "Whether server-side encryption is enabled for the bucket"
  value       = true
}

output "bucket_encryption_algorithm" {
  description = "The server-side encryption algorithm used"
  value       = var.kms_key_id != null ? "aws:kms" : "AES256"
}

output "kms_key_id" {
  description = "The KMS key ID used for encryption (if applicable)"
  value       = var.kms_key_id
}
