data "archive_file" "analytics_api" {
  type        = "zip"
  source_dir  = "${path.module}/../../functions/analytics_api"
  output_path = "${path.module}/analytics_api.zip"

  excludes = [
    ".pytest_cache",
    "tests",
    "examples",
    "__pycache__",
    "repositories/__pycache__",
    "services/__pycache__",
    "utils/__pycache__"
  ]
}

resource "aws_lambda_function" "analytics_api" {
  function_name = "olist-analytics-api-${var.environment}"
  description   = "Analytics API for Olist gold data via Athena"

  role    = aws_iam_role.analytics_lambda.arn
  handler = "handler.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.analytics_api.output_path
  source_code_hash = data.archive_file.analytics_api.output_base64sha256

  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      ATHENA_DATABASE        = local.gold_database
      ATHENA_OUTPUT_LOCATION = "s3://${var.data_bucket_name}/athena/query-results/"
    }
  }

  depends_on = [
    aws_iam_role_policy.analytics_lambda_access
  ]
}