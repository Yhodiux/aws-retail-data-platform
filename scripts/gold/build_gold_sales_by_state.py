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
logger.info("Starting Gold job: sales_by_state")


customers_path = SILVER_BASE_PATH + "/customers/"
orders_path = SILVER_BASE_PATH + "/orders/"
order_items_path = SILVER_BASE_PATH + "/order_items/"
gold_output_path = GOLD_BASE_PATH + "/sales_by_state/"

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
log_dataframe_count(sales_by_state_df, logger, "sales_by_state")
write_parquet(sales_by_state_df,gold_output_path,mode="overwrite",partitions=1)

job.commit()