import sys
from common.config import SILVER_BASE_PATH, GOLD_BASE_PATH
from common.logger import get_logger
from common.gold_transformations import build_sales_by_payment_type
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
logger.info("Starting Gold job: sales_by_payment_type")

orders_path = SILVER_BASE_PATH + "/orders/"
gold_output_path = GOLD_BASE_PATH + "/sales_by_payment_type/"
payments_path = SILVER_BASE_PATH + "/payments/"

payments_df = spark.read.parquet(payments_path)
orders_df = spark.read.parquet(orders_path)

sales_by_payment_type_df = build_sales_by_payment_type(
    orders_df,
    payments_df,
)
log_dataframe_count(sales_by_payment_type_df, logger, "sales_by_payment_type")
write_parquet(sales_by_payment_type_df,gold_output_path,mode="overwrite",partitions=1)

job.commit()
