resource "aws_sns_topic" "glue_failures" {
  name         = "olist-data-platform-alerts"
  display_name = "OLIST ALERTS"
}

# The confirmed email subscription remains outside Terraform so its endpoint is
# not stored in Git or replaced during the initial migration.

resource "aws_cloudwatch_event_rule" "glue_failures" {
  name = "olist-glue-data-quality-failure-alert"

  event_pattern = jsonencode({
    source      = ["aws.glue"]
    detail-type = ["Glue Job State Change"]
    detail = {
      jobName = ["olist-data-quality-gold-job"]
      state   = ["FAILED"]
    }
  })
}

resource "aws_cloudwatch_event_target" "glue_failures" {
  rule      = aws_cloudwatch_event_rule.glue_failures.name
  target_id = "Id49f38e38-decb-45d2-9461-265f4127a073"
  arn       = aws_sns_topic.glue_failures.arn
  role_arn  = data.aws_iam_role.eventbridge_sns.arn
}
