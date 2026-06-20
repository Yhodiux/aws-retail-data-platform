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
