import sys
from common.config import SILVER_BASE_PATH, GOLD_BASE_PATH
from common.logger import get_logger
from common.utils import log_dataframe_count, write_parquet
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, countDistinct, sum as spark_sum, round

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

top_customers_df = (
    customers_df.alias("c")
    .join(orders_df.alias("o"), col("c.customer_id") == col("o.customer_id"), "inner")
    .join(payments_df.alias("p"), col("o.order_id") == col("p.order_id"), "inner")
    .groupBy(
        col("c.customer_unique_id").alias("customer_unique_id"),
        col("c.customer_state").alias("customer_state")
    )
    .agg(
        countDistinct(col("o.order_id")).alias("total_orders"),
        spark_sum(col("p.payment_value")).alias("total_sales")
    )
    .withColumn("total_sales", round(col("total_sales"), 2))
    .withColumn("avg_ticket", round(col("total_sales") / col("total_orders"), 2))
    .orderBy(col("total_sales").desc())
)
log_dataframe_count(top_customers_df, logger, "top_customers")
write_parquet(top_customers_df,gold_output_path,mode="overwrite",partitions=1)

job.commit()