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

SELECT * FROM sales_by_category
ORDER BY total_sales DESC;

SELECT * FROM sales_by_payment_type
ORDER BY total_sales DESC;

SELECT * FROM top_sellers
ORDER BY total_sales DESC;

SELECT * FROM top_customers
ORDER BY total_sales DESC;