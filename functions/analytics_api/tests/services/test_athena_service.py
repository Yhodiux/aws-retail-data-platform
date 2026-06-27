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