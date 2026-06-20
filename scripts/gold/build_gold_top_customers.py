import sys
from common.config import SILVER_BASE_PATH, GOLD_BASE_PATH
from common.logger import get_logger
from common.gold_transformations import build_top_customers
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
logger.info("Starting Gold job: top_customers")

customers_path = SILVER_BASE_PATH + "/customers/"
orders_path = SILVER_BASE_PATH + "/orders/"
payments_path = SILVER_BASE_PATH + "/payments/"
gold_output_path = GOLD_BASE_PATH + "/top_customers/"

customers_df = spark.read.parquet(customers_path)
orders_df = spark.read.parquet(orders_path)
payments_df = spark.read.parquet(payments_path)

top_customers_df = build_top_customers(
    customers_df,
    orders_df,
    payments_df,
)
log_dataframe_count(top_customers_df, logger, "top_customers")
write_parquet(top_customers_df,gold_output_path,mode="overwrite",partitions=1)

job.commit()
