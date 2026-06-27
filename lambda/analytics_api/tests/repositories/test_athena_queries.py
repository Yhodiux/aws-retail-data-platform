from repositories.athena_queries import AthenaQueries

def test_sales_by_state_query():
    query = AthenaQueries.sales_by_state()

    assert isinstance(query, str)
    assert "SELECT" in query.upper()
    assert "FROM olist_gold_db.sales_by_state" in query
    assert "ORDER BY total_sales DESC" in query