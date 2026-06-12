import sys
from common.config import SILVER_BASE_PATH, GOLD_BASE_PATH
from common.logger import get_logger
from common.utils import log_dataframe_count, write_parquet
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

logger = get_logger(args["JOB_NAME"])
logger.info("Starting Gold job: sales_by_category")

orders_path = SILVER_BASE_PATH + "/orders/"
order_items_path = SILVER_BASE_PATH + "/order_items/"
products_path = SILVER_BASE_PATH + "/products/"
gold_output_path = GOLD_BASE_PATH + "/sales_by_category/"

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
log_dataframe_count(sales_by_category_df, logger, "sales_by_category")
write_parquet(sales_by_category_df,gold_output_path,mode="overwrite",partitions=1)
job.commit()