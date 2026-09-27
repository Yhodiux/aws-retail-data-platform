resource "aws_apigatewayv2_api" "analytics" {
  name          = "olist-analytics-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET"]
    allow_headers = ["content-type"]
  }
}

resource "aws_apigatewayv2_integration" "analytics_lambda" {
  api_id = aws_apigatewayv2_api.analytics.id

  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.analytics_api.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "analytics" {
  api_id = aws_apigatewayv2_api.analytics.id

  route_key = "GET /analytics"
  target    = "integrations/${aws_apigatewayv2_integration.analytics_lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.analytics.id

  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analytics_api.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.analytics.execution_arn}/*/*"
}

output "analytics_api_url" {
  description = "Base URL for the Olist Analytics HTTP API"
  value       = "${aws_apigatewayv2_api.analytics.api_endpoint}/analytics"
}