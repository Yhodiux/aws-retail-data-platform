import json
from unittest.mock import patch

from handler import lambda_handler


@patch("handler.AthenaService")
def test_lambda_handler_default_operation(mock_athena_service):
    mock_service = mock_athena_service.return_value

    mock_service.sales_by_state.return_value = [
        {
            "customer_state": "SP",
            "total_orders": "41375",
            "total_sales": "5202955.05",
        }
    ]

    response = lambda_handler({}, None)

    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"

    body = json.loads(response["body"])

    assert len(body) == 1
    assert body[0]["customer_state"] == "SP"

    mock_service.sales_by_state.assert_called_once_with(limit=10)


@patch("handler.AthenaService")
def test_lambda_handler_sales_by_category(mock_athena_service):
    mock_service = mock_athena_service.return_value
    mock_service.sales_by_category.return_value = []

    response = lambda_handler(
        {"operation": "sales_by_category", "limit": 5},
        None,
    )

    assert response["statusCode"] == 200
    mock_service.sales_by_category.assert_called_once_with(limit=5)


@patch("handler.AthenaService")
def test_lambda_handler_sales_by_payment_type(mock_athena_service):
    mock_service = mock_athena_service.return_value
    mock_service.sales_by_payment_type.return_value = []

    response = lambda_handler(
        {"operation": "sales_by_payment_type", "limit": 7},
        None,
    )

    assert response["statusCode"] == 200
    mock_service.sales_by_payment_type.assert_called_once_with(limit=7)


@patch("handler.AthenaService")
def test_lambda_handler_top_customers(mock_athena_service):
    mock_service = mock_athena_service.return_value
    mock_service.top_customers.return_value = []

    response = lambda_handler(
        {"operation": "top_customers", "limit": 3},
        None,
    )

    assert response["statusCode"] == 200
    mock_service.top_customers.assert_called_once_with(limit=3)


@patch("handler.AthenaService")
def test_lambda_handler_top_sellers(mock_athena_service):
    mock_service = mock_athena_service.return_value
    mock_service.top_sellers.return_value = []

    response = lambda_handler(
        {"operation": "top_sellers"},
        None,
    )

    assert response["statusCode"] == 200
    mock_service.top_sellers.assert_called_once_with(limit=10)


@patch("handler.AthenaService")
def test_lambda_handler_unsupported_operation(mock_athena_service):
    response = lambda_handler(
        {"operation": "does_not_exist"},
        None,
    )

    assert response["statusCode"] == 400
    assert response["headers"]["Content-Type"] == "application/json"

    body = json.loads(response["body"])

    assert body["error"] == "Unsupported operation"
    assert body["operation"] == "does_not_exist"

    mock_athena_service.assert_not_called()

@patch("handler.AthenaService")
def test_lambda_handler_accepts_string_limit(mock_athena_service):
    mock_service = mock_athena_service.return_value
    mock_service.sales_by_state.return_value = []

    response = lambda_handler(
        {"limit": "5"},
        None,
    )

    assert response["statusCode"] == 200
    mock_service.sales_by_state.assert_called_once_with(limit=5)


@patch("handler.AthenaService")
def test_lambda_handler_rejects_non_integer_limit(mock_athena_service):
    response = lambda_handler(
        {"limit": "abc"},
        None,
    )

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "limit must be an integer"
    mock_athena_service.assert_not_called()


@patch("handler.AthenaService")
def test_lambda_handler_rejects_zero_limit(mock_athena_service):
    response = lambda_handler(
        {"limit": 0},
        None,
    )

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "limit must be between 1 and 100"
    mock_athena_service.assert_not_called()


@patch("handler.AthenaService")
def test_lambda_handler_accepts_string_limit(mock_athena_service):
    mock_service = mock_athena_service.return_value
    mock_service.sales_by_state.return_value = []

    response = lambda_handler(
        {"limit": "5"},
        None,
    )

    assert response["statusCode"] == 200
    mock_service.sales_by_state.assert_called_once_with(limit=5)


@patch("handler.AthenaService")
def test_lambda_handler_rejects_non_integer_limit(mock_athena_service):
    response = lambda_handler(
        {"limit": "abc"},
        None,
    )

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "limit must be an integer"
    mock_athena_service.assert_not_called()


@patch("handler.AthenaService")
def test_lambda_handler_rejects_zero_limit(mock_athena_service):
    response = lambda_handler(
        {"limit": 0},
        None,
    )

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "limit must be between 1 and 100"
    mock_athena_service.assert_not_called()


@patch("handler.AthenaService")
def test_lambda_handler_rejects_limit_above_maximum(mock_athena_service):
    response = lambda_handler(
        {"limit": 101},
        None,
    )

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "limit must be between 1 and 100"
    mock_athena_service.assert_not_called()

@patch("handler.AthenaService")
def test_lambda_handler_api_gateway_query_parameters(mock_athena_service):
    mock_service = mock_athena_service.return_value
    mock_service.top_sellers.return_value = []

    event = {
        "version": "2.0",
        "queryStringParameters": {
            "operation": "top_sellers",
            "limit": "5",
        },
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_service.top_sellers.assert_called_once_with(limit=5)
