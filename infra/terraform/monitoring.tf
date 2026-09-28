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

# -----------------------------------------------------------------------------
# Analytics API monitoring
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "analytics_api_errors" {
  alarm_name        = "olist-analytics-api-errors-${var.environment}"
  alarm_description = "Alerts when the Analytics API Lambda reports execution errors."

  namespace   = "AWS/Lambda"
  metric_name = "Errors"
  statistic   = "Sum"

  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"

  dimensions = {
    FunctionName = aws_lambda_function.analytics_api.function_name
  }

  alarm_actions = [
    aws_sns_topic.glue_failures.arn
  ]

  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "analytics_api_duration" {
  alarm_name        = "olist-analytics-api-duration-${var.environment}"
  alarm_description = "Alerts when the Analytics API Lambda execution duration is unusually high."

  namespace   = "AWS/Lambda"
  metric_name = "Duration"
  statistic   = "Maximum"

  period              = 300
  evaluation_periods  = 1
  threshold           = 20000
  comparison_operator = "GreaterThanOrEqualToThreshold"

  dimensions = {
    FunctionName = aws_lambda_function.analytics_api.function_name
  }

  alarm_actions = [
    aws_sns_topic.glue_failures.arn
  ]

  treat_missing_data = "notBreaching"
}