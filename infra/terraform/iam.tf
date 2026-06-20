data "aws_iam_role" "glue" {
  name = "AWSGlueServiceRole"
}

data "aws_iam_role" "eventbridge_sns" {
  name = "Amazon_EventBridge_Invoke_Sns_2055355687"
}
