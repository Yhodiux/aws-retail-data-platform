data "aws_iam_role" "glue" {
  name = "AWSGlueServiceRole"
}

data "aws_iam_role" "eventbridge_sns" {
  name = "Amazon_EventBridge_Invoke_Sns_2055355687"
}

data "aws_iam_policy_document" "glue_data_bucket" {
  statement {
    sid = "ListDataBucket"
    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket",
    ]
    resources = [aws_s3_bucket.data.arn]
  }

  statement {
    sid     = "ReadInputsAndArtifacts"
    actions = ["s3:GetObject"]
    resources = [
      "${aws_s3_bucket.data.arn}/raw/*",
      "${aws_s3_bucket.data.arn}/scripts/*",
      "${aws_s3_bucket.data.arn}/libs/*",
    ]
  }

  statement {
    sid = "ManagePipelineOutputs"
    actions = [
      "s3:AbortMultipartUpload",
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:ListMultipartUploadParts",
      "s3:PutObject",
    ]
    resources = [
      "${aws_s3_bucket.data.arn}/silver/*",
      "${aws_s3_bucket.data.arn}/gold/*",
      "${aws_s3_bucket.data.arn}/logs/*",
      "${aws_s3_bucket.data.arn}/temp/*",
    ]
  }
}

resource "aws_iam_role_policy" "glue_data_bucket" {
  name   = "olist-retail-data-bucket-access"
  role   = data.aws_iam_role.glue.name
  policy = data.aws_iam_policy_document.glue_data_bucket.json
}
# -----------------------------------------------------------------------------
# Analytics API Lambda
# -----------------------------------------------------------------------------

data "aws_iam_policy_document" "analytics_lambda_assume_role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type = "Service"

      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "analytics_lambda" {
  name = "olist-analytics-lambda-${var.environment}"

  assume_role_policy = data.aws_iam_policy_document.analytics_lambda_assume_role.json
}

data "aws_iam_policy_document" "analytics_lambda_access" {

  # Ejecutar y consultar queries en Athena
  statement {
    sid = "AthenaQueryAccess"

    actions = [
      "athena:StartQueryExecution",
      "athena:GetQueryExecution",
      "athena:GetQueryResults"
    ]

    resources = ["*"]
  }

  # Athena necesita consultar el Glue Data Catalog
  statement {
    sid = "GlueCatalogRead"

    actions = [
      "glue:GetDatabase",
      "glue:GetDatabases",
      "glue:GetTable",
      "glue:GetTables",
      "glue:GetPartition",
      "glue:GetPartitions"
    ]

    resources = ["*"]
  }

  # Leer los datos Gold consultados por Athena
  statement {
    sid = "ReadGoldData"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.data.arn}/gold/*"
    ]
  }

  # Athena necesita acceso al bucket y a su ubicación
  statement {
    sid = "AthenaBucketAccess"

    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.data.arn
    ]
  }

  # Guardar y leer los resultados producidos por Athena
  statement {
    sid = "AthenaQueryResults"

    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.data.arn}/athena/query-results/*"
    ]
  }
}

resource "aws_iam_role_policy" "analytics_lambda_access" {
  name   = "olist-analytics-lambda-access"
  role   = aws_iam_role.analytics_lambda.name
  policy = data.aws_iam_policy_document.analytics_lambda_access.json
}