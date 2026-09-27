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

    @staticmethod
    def sales_by_category(limit: int = 10) -> str:
        return f"""
        SELECT
            product_category_name,
            total_orders,
            total_items,
            total_sales,
            avg_price,
            delivered_orders,
            delivered_items,
            delivered_product_revenue,
            delivered_freight_value,
            delivered_avg_item_price,
            delivered_avg_ticket
        FROM olist_gold_db.sales_by_category
        ORDER BY total_sales DESC
        LIMIT {limit}
        """

    @staticmethod
    def sales_by_payment_type(limit: int = 10) -> str:
        return f"""
        SELECT
            payment_type,
            total_orders,
            total_sales,
            avg_payment_value,
            total_payment_records,
            delivered_orders,
            delivered_payment_records,
            delivered_payment_value,
            delivered_avg_payment_value,
            delivered_avg_order_payment_value
        FROM olist_gold_db.sales_by_payment_type
        ORDER BY total_sales DESC
        LIMIT {limit}
        """

    @staticmethod
    def top_customers(limit: int = 10) -> str:
        return f"""
        SELECT
            customer_unique_id,
            customer_state,
            total_orders,
            total_sales,
            total_payment_records,
            delivered_orders,
            delivered_payment_records,
            delivered_payment_value,
            delivered_first_purchase_at,
            delivered_last_purchase_at,
            avg_ticket,
            delivered_avg_order_payment_value
        FROM olist_gold_db.top_customers
        ORDER BY delivered_payment_value DESC
        LIMIT {limit}
        """

    @staticmethod
    def top_sellers(limit: int = 10) -> str:
        return f"""
        SELECT
            seller_id,
            seller_state,
            total_orders,
            total_items,
            total_sales,
            delivered_orders,
            delivered_items,
            delivered_product_revenue,
            delivered_freight_value,
            delivered_avg_item_price,
            delivered_first_sale_at,
            delivered_last_sale_at,
            delivered_avg_order_product_revenue
        FROM olist_gold_db.top_sellers
        ORDER BY delivered_product_revenue DESC
        LIMIT {limit}
        """
