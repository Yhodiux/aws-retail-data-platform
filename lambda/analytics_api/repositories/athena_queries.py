class AthenaQueries:
    @staticmethod
    def sales_by_state(limit: int = 10) -> str:
        return f"""
        SELECT
            customer_state,
            total_orders,
            total_items,
            total_sales,
            avg_ticket
        FROM olist_gold_db.sales_by_state
        ORDER BY total_sales DESC
        LIMIT {limit}
        """