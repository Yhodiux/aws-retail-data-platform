import sys
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

bucket = "s3://olist-data-engineering-otto"

orders_path = f"{bucket}/silver/orders/"
payments_path = f"{bucket}/silver/payments/"

gold_output_path = f"{bucket}/gold/sales_by_payment_type/"

orders_df = spark.read.parquet(orders_path)
payments_df = spark.read.parquet(payments_path)

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

sales_by_payment_type_df.coalesce(1).write.mode("overwrite").parquet(gold_output_path)

job.commit()