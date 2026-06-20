import sys
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, count, lit, current_timestamp

from common.config import GOLD_DATABASE, LOGS_BASE_PATH

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

QUALITY_RULES = {
    "sales_by_category": {
        "not_null": ["product_category_name"],
        "non_negative": [
            "total_sales",
            "total_items",
            "total_orders",
            "delivered_product_revenue",
            "delivered_freight_value",
            "delivered_avg_item_price",
            "delivered_avg_ticket",
            "delivered_items",
            "delivered_orders"
        ],
        "less_than_or_equal": [
            ("delivered_orders", "total_orders"),
            ("delivered_items", "total_items")
        ]
    },
    "sales_by_payment_type": {
        "not_null": ["payment_type"],
        "non_negative": [
            "total_sales",
            "total_orders",
            "total_payment_records",
            "delivered_orders",
            "delivered_payment_records",
            "delivered_payment_value",
            "delivered_avg_payment_value",
            "delivered_avg_order_payment_value"
        ],
        "less_than_or_equal": [
            ("delivered_orders", "total_orders"),
            ("delivered_payment_records", "total_payment_records")
        ]
    },
    "sales_by_state": {
        "not_null": ["customer_state"],
        "non_negative": [
            "total_sales",
            "total_freight",
            "total_items",
            "total_orders",
            "delivered_product_revenue",
            "delivered_freight_value",
            "delivered_avg_ticket",
            "delivered_items",
            "delivered_orders"
        ],
        "less_than_or_equal": [
            ("delivered_orders", "total_orders"),
            ("delivered_items", "total_items")
        ]
    },
    "top_customers": {
        "not_null": ["customer_unique_id"],
        "non_negative": [
            "total_sales",
            "total_orders",
            "total_payment_records",
            "delivered_orders",
            "delivered_payment_records",
            "delivered_payment_value",
            "delivered_avg_order_payment_value"
        ],
        "less_than_or_equal": [
            ("delivered_orders", "total_orders"),
            ("delivered_payment_records", "total_payment_records"),
            ("delivered_first_purchase_at", "delivered_last_purchase_at")
        ]
    },
    "top_sellers": {
        "not_null": ["seller_id"],
        "non_negative": [
            "total_sales",
            "total_items",
            "total_orders",
            "delivered_orders",
            "delivered_items",
            "delivered_product_revenue",
            "delivered_freight_value",
            "delivered_avg_item_price",
            "delivered_avg_order_product_revenue"
        ],
        "less_than_or_equal": [
            ("delivered_orders", "total_orders"),
            ("delivered_items", "total_items"),
            ("delivered_first_sale_at", "delivered_last_sale_at")
        ]
    }
}


def read_table(table_name):
    return spark.table(f"{GOLD_DATABASE}.{table_name}")


def validate_table(table_name, rules):
    print(f"Validating table: {table_name}")

    df = read_table(table_name)
    total_records = df.count()

    errors = []

    if total_records == 0:
        errors.append(f"{table_name}: table is empty")

    for column_name in rules.get("not_null", []):
        null_count = df.filter(col(column_name).isNull()).count()
        if null_count > 0:
            errors.append(f"{table_name}: column {column_name} has {null_count} null values")

    for column_name in rules.get("non_negative", []):
        negative_count = df.filter(col(column_name) < 0).count()
        if negative_count > 0:
            errors.append(f"{table_name}: column {column_name} has {negative_count} negative values")

    for lower_column, upper_column in rules.get("less_than_or_equal", []):
        invalid_count = df.filter(col(lower_column) > col(upper_column)).count()
        if invalid_count > 0:
            errors.append(
                f"{table_name}: {invalid_count} rows have "
                f"{lower_column} greater than {upper_column}"
            )

    status = "FAIL" if errors else "PASS"

    print(f"{table_name} status: {status}")
    print(f"{table_name} records: {total_records}")

    return {
        "table_name": table_name,
        "status": status,
        "total_records": total_records,
        "errors": " | ".join(errors) if errors else ""
    }


results = []

for table_name, rules in QUALITY_RULES.items():
    results.append(validate_table(table_name, rules))

results_df = spark.createDataFrame(results)
results_df = results_df.withColumn("execution_timestamp", current_timestamp())

results_df.show(truncate=False)

output_path = f"{LOGS_BASE_PATH}/data-quality/gold/"

results_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)

failed = [row for row in results if row["status"] == "FAIL"]

if failed:
    raise Exception(f"Data Quality validation failed: {failed}")

print("Data Quality validation completed successfully.")
