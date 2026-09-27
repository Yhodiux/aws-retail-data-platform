import json
from unittest.mock import patch

from handler import lambda_handler


@patch("handler.AthenaService")
def test_lambda_handler_success(mock_athena_service):
    mock_service = mock_athena_service.return_value

    mock_service.sales_by_state.return_value = [
        {
            "customer_state": "SP",
            "total_orders": "41375",
            "total_sales": "5202955.05"
        }
    ]

    response = lambda_handler({}, None)

    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"

    body = json.loads(response["body"])

    assert len(body) == 1
    assert body[0]["customer_state"] == "SP"

    mock_service.sales_by_state.assert_called_once_with(limit=10)