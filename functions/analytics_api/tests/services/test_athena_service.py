from unittest.mock import patch

from repositories.athena_queries import AthenaQueries
from services.athena_service import AthenaService


def test_athena_service_runs_sales_by_state_query():
    query = AthenaQueries.sales_by_state(limit=5)

    service = AthenaService()
    results = service.run_query(query)

    assert isinstance(results, list)
    assert len(results) > 0

    first_row = results[0]

    assert "customer_state" in first_row
    assert "total_orders" in first_row
    assert "total_items" in first_row
    assert "total_sales" in first_row
    assert "avg_ticket" in first_row


@patch.object(AthenaService, "run_query")
def test_sales_by_state_delegates_to_run_query(mock_run_query):
    mock_run_query.return_value = []

    service = AthenaService()
    result = service.sales_by_state(limit=5)

    mock_run_query.assert_called_once_with(
        AthenaQueries.sales_by_state(limit=5)
    )
    assert result == []


@patch.object(AthenaService, "run_query")
def test_sales_by_category_delegates_to_run_query(mock_run_query):
    mock_run_query.return_value = []

    service = AthenaService()
    result = service.sales_by_category(limit=5)

    mock_run_query.assert_called_once_with(
        AthenaQueries.sales_by_category(limit=5)
    )
    assert result == []


@patch.object(AthenaService, "run_query")
def test_sales_by_payment_type_delegates_to_run_query(mock_run_query):
    mock_run_query.return_value = []

    service = AthenaService()
    result = service.sales_by_payment_type(limit=5)

    mock_run_query.assert_called_once_with(
        AthenaQueries.sales_by_payment_type(limit=5)
    )
    assert result == []


@patch.object(AthenaService, "run_query")
def test_top_customers_delegates_to_run_query(mock_run_query):
    mock_run_query.return_value = []

    service = AthenaService()
    result = service.top_customers(limit=5)

    mock_run_query.assert_called_once_with(
        AthenaQueries.top_customers(limit=5)
    )
    assert result == []


@patch.object(AthenaService, "run_query")
def test_top_sellers_delegates_to_run_query(mock_run_query):
    mock_run_query.return_value = []

    service = AthenaService()
    result = service.top_sellers(limit=5)

    mock_run_query.assert_called_once_with(
        AthenaQueries.top_sellers(limit=5)
    )
    assert result == []