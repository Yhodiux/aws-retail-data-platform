variable "aws_region" {
  description = "AWS Region for all project resources."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Optional local AWS shared-config profile. Leave null in CI."
  type        = string
  default     = null
  nullable    = true
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.environment))
    error_message = "environment must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "project_name" {
  description = "Resource-name prefix."
  type        = string
  default     = "olist-retail"
}

variable "data_bucket_name" {
  description = "Globally unique S3 data and artifact bucket name."
  type        = string
  default     = "olist-retail-data-dev-us-east-1-793a6f"
}

variable "glue_version" {
  description = "AWS Glue runtime version. Glue 5.0 aligns with local Spark 3.5 tests."
  type        = string
  default     = "5.1"
}

variable "worker_type" {
  description = "Glue worker type."
  type        = string
  default     = "G.1X"
}

variable "number_of_workers" {
  description = "Workers per Glue job."
  type        = number
  default     = 2
}

variable "notification_email" {
  description = "Optional email endpoint for Glue failure notifications."
  type        = string
  default     = null
  nullable    = true
}

variable "force_destroy_bucket" {
  description = "Allow Terraform to delete a non-empty project bucket. Keep false outside disposable environments."
  type        = bool
  default     = false
}
