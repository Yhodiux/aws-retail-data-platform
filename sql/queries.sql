-- Silver Validation

SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_items;
SELECT COUNT(*) FROM payments;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM sellers;

-- Gold Validation

SHOW TABLES IN olist_gold_db;

SELECT * FROM sales_by_state
ORDER BY total_sales DESC;

-- sales_by_state delivered-metric validation
SELECT
    SUM(total_orders) AS total_orders,
    SUM(delivered_orders) AS delivered_orders,
    ROUND(SUM(total_sales), 2) AS legacy_total_sales,
    ROUND(SUM(delivered_product_revenue), 2) AS delivered_product_revenue,
    ROUND(SUM(delivered_freight_value), 2) AS delivered_freight_value
FROM sales_by_state;

SELECT *
FROM sales_by_state
WHERE delivered_orders > total_orders
   OR delivered_items > total_items
   OR delivered_product_revenue < 0
   OR delivered_freight_value < 0;

SELECT * FROM sales_by_category
ORDER BY total_sales DESC;

-- sales_by_category delivered-metric validation
SELECT
    COUNT(*) AS category_count,
    SUM(total_items) AS total_items,
    SUM(delivered_items) AS delivered_items,
    SUM(delivered_orders) AS delivered_order_category_pairs,
    ROUND(SUM(total_sales), 2) AS legacy_total_sales,
    ROUND(SUM(delivered_product_revenue), 2) AS delivered_product_revenue,
    ROUND(SUM(delivered_freight_value), 2) AS delivered_freight_value
FROM sales_by_category;

SELECT *
FROM sales_by_category
WHERE delivered_orders > total_orders
   OR delivered_items > total_items
   OR delivered_product_revenue < 0
   OR delivered_freight_value < 0;

SELECT * FROM sales_by_payment_type
ORDER BY total_sales DESC;

-- sales_by_payment_type delivered-metric validation
SELECT
    COUNT(*) AS payment_type_count,
    COUNT_IF(delivered_orders > 0) AS delivered_payment_type_count,
    SUM(total_payment_records) AS total_payment_records,
    SUM(delivered_payment_records) AS delivered_payment_records,
    SUM(delivered_orders) AS delivered_order_payment_type_pairs,
    ROUND(SUM(total_sales), 2) AS legacy_total_sales,
    ROUND(SUM(delivered_payment_value), 2) AS delivered_payment_value
FROM sales_by_payment_type;

SELECT *
FROM sales_by_payment_type
WHERE delivered_orders > total_orders
   OR delivered_payment_records > total_payment_records
   OR delivered_payment_value < 0;

SELECT * FROM top_sellers
ORDER BY total_sales DESC;

-- top_sellers delivered-metric validation
SELECT
    COUNT(*) AS seller_state_rows,
    COUNT_IF(delivered_orders > 0) AS sellers_with_delivered_orders,
    SUM(delivered_orders) AS delivered_order_seller_pairs,
    SUM(delivered_items) AS delivered_items,
    ROUND(SUM(delivered_product_revenue), 2) AS delivered_product_revenue,
    ROUND(SUM(delivered_freight_value), 2) AS delivered_freight_value,
    MIN(delivered_first_sale_at) AS first_delivered_sale_at,
    MAX(delivered_last_sale_at) AS last_delivered_sale_at
FROM top_sellers;

SELECT *
FROM top_sellers
WHERE delivered_orders > total_orders
   OR delivered_items > total_items
   OR delivered_product_revenue < 0
   OR delivered_freight_value < 0
   OR delivered_first_sale_at > delivered_last_sale_at;

SELECT * FROM top_customers
ORDER BY total_sales DESC;

-- top_customers delivered-metric validation
SELECT
    COUNT(*) AS customer_state_rows,
    COUNT_IF(delivered_orders > 0) AS customers_with_delivered_orders,
    SUM(delivered_orders) AS delivered_orders,
    SUM(delivered_payment_records) AS delivered_payment_records,
    ROUND(SUM(delivered_payment_value), 2) AS delivered_payment_value,
    MIN(delivered_first_purchase_at) AS first_delivered_purchase_at,
    MAX(delivered_last_purchase_at) AS last_delivered_purchase_at
FROM top_customers;

SELECT *
FROM top_customers
WHERE delivered_orders > total_orders
   OR delivered_payment_records > total_payment_records
   OR delivered_payment_value < 0
   OR delivered_first_purchase_at > delivered_last_purchase_at;
