import sys
from common.config import SILVER_BASE_PATH, GOLD_BASE_PATH
from common.logger import get_logger
from common.utils import log_dataframe_count, write_parquet
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

logger = get_logger(args["JOB_NAME"])
logger.info("Starting Gold job: top_sellers")

orders_path = SILVER_BASE_PATH + "/orders/"
order_items_path = SILVER_BASE_PATH + "/order_items/"
sellers_path = SILVER_BASE_PATH + "/sellers/"
gold_output_path = GOLD_BASE_PATH + "/top_sellers/"

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
log_dataframe_count(top_sellers_df, logger, "top_sellers")
write_parquet(top_sellers_df,gold_output_path,mode="overwrite",partitions=1)
job.commit()