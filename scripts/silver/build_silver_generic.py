import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, trim, upper, to_timestamp

args = getResolvedOptions(sys.argv, ["JOB_NAME", "TABLE_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

table_name = args["TABLE_NAME"]

raw_path = f"s3://olist-data-engineering-otto/raw/{table_name}/"
silver_path = f"s3://olist-data-engineering-otto/silver/{table_name}/"

df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .option("delimiter", ",")
    .csv(raw_path)
)

for c in df.columns:
    if dict(df.dtypes)[c] == "string":
        df = df.withColumn(c, trim(col(c)))

if table_name == "customers":
    df = (
        df
        .withColumn("customer_city", upper(col("customer_city")))
        .withColumn("customer_state", upper(col("customer_state")))
        .dropDuplicates(["customer_id"])
    )

elif table_name == "orders":
    timestamp_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for c in timestamp_cols:
        df = df.withColumn(c, to_timestamp(col(c)))

    df = df.dropDuplicates(["order_id"])

df.write.mode("overwrite").parquet(silver_path)

job.commit()