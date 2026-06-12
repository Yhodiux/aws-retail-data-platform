import sys
from common.config import SILVER_BASE_PATH, GOLD_BASE_PATH
from common.logger import get_logger
from common.utils import log_dataframe_count, write_parquet
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, countDistinct, sum as spark_sum, avg, round

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

logger = get_logger(args["JOB_NAME"])
logger.info("Starting Gold job: sales_by_payment_type")

customers_path = SILVER_BASE_PATH + "/customers/"
orders_path = SILVER_BASE_PATH + "/orders/"
order_items_path = SILVER_BASE_PATH + "/order_items/"
gold_output_path = GOLD_BASE_PATH + "/sales_by_payment_type/"
payments_path = SILVER_BASE_PATH + "/payments/"

payments_df = spark.read.parquet(payments_path)
orders_df = spark.read.parquet(orders_path)
order_items_df = spark.read.parquet(order_items_path)

sales_by_payment_type_df = (
    orders_df.alias("o")
    .join(payments_df.alias("p"), col("o.order_id") == col("p.order_id"), "inner")
    .groupBy(col("p.payment_type").alias("payment_type"))
    .agg(
        countDistinct(col("o.order_id")).alias("total_orders"),
        spark_sum(col("p.payment_value")).alias("total_sales"),
        round(avg(col("p.payment_value")), 2).alias("avg_payment_value")
    )
    .orderBy(col("total_sales").desc())
)
log_dataframe_count(sales_by_payment_type_df, logger, "sales_by_payment_type")
write_parquet(sales_by_payment_type_df,gold_output_path,mode="overwrite",partitions=1)

job.commit()