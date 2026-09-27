from repositories.athena_queries import AthenaQueries

def test_sales_by_state_query():
    query = AthenaQueries.sales_by_state()

    assert isinstance(query, str)
    assert "SELECT" in query.upper()
    assert "FROM olist_gold_db.sales_by_state" in query
    assert "ORDER BY total_sales DESC" in query

def test_sales_by_category_query():
    query = AthenaQueries.sales_by_category()

    assert isinstance(query, str)
    assert "SELECT" in query.upper()
    assert "FROM olist_gold_db.sales_by_category" in query
    assert "product_category_name" in query
    assert "delivered_product_revenue" in query
    assert "ORDER BY total_sales DESC" in query

def test_sales_by_payment_type_query():
    query = AthenaQueries.sales_by_payment_type()

    assert isinstance(query, str)
    assert "SELECT" in query.upper()
    assert "FROM olist_gold_db.sales_by_payment_type" in query
    assert "payment_type" in query
    assert "delivered_payment_value" in query
    assert "ORDER BY total_sales DESC" in query

def test_top_customers_query():
    query = AthenaQueries.top_customers()

    assert isinstance(query, str)
    assert "SELECT" in query.upper()
    assert "FROM olist_gold_db.top_customers" in query
    assert "customer_unique_id" in query
    assert "delivered_payment_value" in query
    assert "ORDER BY delivered_payment_value DESC" in query

def test_top_sellers_query():
    query = AthenaQueries.top_sellers()

    assert isinstance(query, str)
    assert "SELECT" in query.upper()
    assert "FROM olist_gold_db.top_sellers" in query
    assert "seller_id" in query
    assert "delivered_product_revenue" in query
    assert "ORDER BY delivered_product_revenue DESC" in query
