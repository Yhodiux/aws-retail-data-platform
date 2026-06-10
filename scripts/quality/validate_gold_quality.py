import sys
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, count, lit, current_timestamp

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

DATABASE = "olist_gold_db"

QUALITY_RULES = {
    "sales_by_category": {
        "not_null": ["product_category_name"],
        "non_negative": ["total_sales", "total_items", "total_orders"]
    },
    "sales_by_payment_type": {
        "not_null": ["payment_type"],
        "non_negative": ["total_sales", "total_orders"]
    },
    "sales_by_state": {
        "not_null": ["customer_state"],
        "non_negative": ["total_sales", "total_items", "total_orders"]
    },
    "top_customers": {
        "not_null": ["customer_unique_id"],
        "non_negative": ["total_sales", "total_orders"]
    },
    "top_sellers": {
        "not_null": ["seller_id"],
        "non_negative": ["total_sales", "total_items", "total_orders"]
    }
}


def read_table(table_name):
    return spark.table(f"{DATABASE}.{table_name}")


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

output_path = "s3://olist-data-engineering-otto/logs/data-quality/gold/"

results_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)

failed = [row for row in results if row["status"] == "FAIL"]

if failed:
    raise Exception(f"Data Quality validation failed: {failed}")

print("Data Quality validation completed successfully.")