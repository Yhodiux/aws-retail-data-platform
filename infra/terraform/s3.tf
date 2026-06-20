resource "aws_s3_bucket" "data" {
  bucket        = var.data_bucket_name
  force_destroy = var.force_destroy_bucket

  tags = {
    Project     = "olist-retail-data-platform"
    Environment = "dev"
    ManagedBy   = "terraform-migration"
  }
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "common_zip" {
  bucket = aws_s3_bucket.data.id
  key    = local.artifact_keys.common_zip
  source = "${path.module}/../../libs/common.zip"
  etag   = filemd5("${path.module}/../../libs/common.zip")
}

resource "aws_s3_object" "silver_generic" {
  bucket = aws_s3_bucket.data.id
  key    = local.artifact_keys.silver_generic
  source = "${path.module}/../../scripts/silver/build_silver_generic.py"
  etag   = filemd5("${path.module}/../../scripts/silver/build_silver_generic.py")
}

resource "aws_s3_object" "gold_scripts" {
  for_each = local.gold_jobs

  bucket = aws_s3_bucket.data.id
  key    = each.value.key
  source = "${path.module}/../../${each.value.source}"
  etag   = filemd5("${path.module}/../../${each.value.source}")
}

resource "aws_s3_object" "gold_quality" {
  bucket = aws_s3_bucket.data.id
  key    = local.artifact_keys.gold_quality
  source = "${path.module}/../../scripts/quality/validate_gold_quality.py"
  etag   = filemd5("${path.module}/../../scripts/quality/validate_gold_quality.py")
}
