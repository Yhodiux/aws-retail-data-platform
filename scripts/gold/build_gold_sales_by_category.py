import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, countDistinct, count, sum as spark_sum, avg, round, coalesce, lit

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

bucket = "s3://olist-data-engineering-otto"

orders_path = f"{bucket}/silver/orders/"
order_items_path = f"{bucket}/silver/order_items/"
products_path = f"{bucket}/silver/products/"

gold_output_path = f"{bucket}/gold/sales_by_category/"

orders_df = spark.read.parquet(orders_path)
order_items_df = spark.read.parquet(order_items_path)
products_df = spark.read.parquet(products_path)

sales_by_category_df = (
    orders_df.alias("o")
    .join(order_items_df.alias("oi"), col("o.order_id") == col("oi.order_id"), "inner")
    .join(products_df.alias("p"), col("oi.product_id") == col("p.product_id"), "left")
    .groupBy(coalesce(col("p.product_category_name"), lit("UNKNOWN")).alias("product_category_name"))
    .agg(
        countDistinct(col("o.order_id")).alias("total_orders"),
        count(col("oi.product_id")).alias("total_items"),
        spark_sum(col("oi.price")).alias("total_sales"),
        round(avg(col("oi.price")), 2).alias("avg_price")
    )
    .orderBy(col("total_sales").desc())
)

sales_by_category_df.coalesce(1).write.mode("overwrite").parquet(gold_output_path)

job.commit()