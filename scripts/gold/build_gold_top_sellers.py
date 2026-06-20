import sys
from common.config import SILVER_BASE_PATH, GOLD_BASE_PATH
from common.logger import get_logger
from common.gold_transformations import build_top_sellers
from common.utils import log_dataframe_count, write_parquet
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

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

top_sellers_df = build_top_sellers(
    orders_df,
    order_items_df,
    sellers_df,
)
log_dataframe_count(top_sellers_df, logger, "top_sellers")
write_parquet(top_sellers_df,gold_output_path,mode="overwrite",partitions=1)
job.commit()
