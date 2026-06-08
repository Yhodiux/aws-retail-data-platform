import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, countDistinct, count, sum as spark_sum, round

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

bucket = "s3://olist-data-engineering-otto"

customers_path = f"{bucket}/silver/customers/"
orders_path = f"{bucket}/silver/orders/"
order_items_path = f"{bucket}/silver/order_items/"

gold_output_path = f"{bucket}/gold/sales_by_state/"

customers_df = spark.read.parquet(customers_path)
orders_df = spark.read.parquet(orders_path)
order_items_df = spark.read.parquet(order_items_path)

sales_by_state_df = (
    orders_df.alias("o")
    .join(customers_df.alias("c"), col("o.customer_id") == col("c.customer_id"), "inner")
    .join(order_items_df.alias("oi"), col("o.order_id") == col("oi.order_id"), "inner")
    .groupBy(col("c.customer_state").alias("customer_state"))
    .agg(
        countDistinct(col("o.order_id")).alias("total_orders"),
        count(col("oi.product_id")).alias("total_items"),
        spark_sum(col("oi.price")).alias("total_sales"),
        spark_sum(col("oi.freight_value")).alias("total_freight")
    )
    .withColumn(
        "avg_ticket",
        round(col("total_sales") / col("total_orders"), 2)
    )
    .orderBy(col("total_sales").desc())
)

sales_by_state_df.coalesce(1).write.mode("overwrite").parquet(gold_output_path)

job.commit()