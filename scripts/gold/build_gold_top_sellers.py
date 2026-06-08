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

orders_path = f"{bucket}/silver/orders/"
order_items_path = f"{bucket}/silver/order_items/"
sellers_path = f"{bucket}/silver/sellers/"

gold_output_path = f"{bucket}/gold/top_sellers/"

orders_df = spark.read.parquet(orders_path)
order_items_df = spark.read.parquet(order_items_path)
sellers_df = spark.read.parquet(sellers_path)

top_sellers_df = (
    orders_df.alias("o")
    .join(order_items_df.alias("oi"), col("o.order_id") == col("oi.order_id"), "inner")
    .join(sellers_df.alias("s"), col("oi.seller_id") == col("s.seller_id"), "left")
    .groupBy(
        col("oi.seller_id").alias("seller_id"),
        col("s.seller_state").alias("seller_state")
    )
    .agg(
        countDistinct(col("o.order_id")).alias("total_orders"),
        count(col("oi.product_id")).alias("total_items"),
        spark_sum(col("oi.price")).alias("total_sales")
    )
    .withColumn("total_sales", round(col("total_sales"), 2))
    .orderBy(col("total_sales").desc())
)

top_sellers_df.coalesce(1).write.mode("overwrite").parquet(gold_output_path)

job.commit()