import sys
from common.config import RAW_BASE_PATH, SILVER_BASE_PATH
from common.data_quality import validate_table_quality
from common.logger import get_logger
from common.schemas import get_table_schema
from common.silver_transformations import (
    apply_silver_transformations,
    normalize_string_columns,
)
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME", "TABLE_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

table_name = args["TABLE_NAME"]
schema = get_table_schema(table_name)
logger = get_logger(args["JOB_NAME"])

raw_path = f"{RAW_BASE_PATH}/{table_name}/"
silver_path = f"{SILVER_BASE_PATH}/{table_name}/"

logger.info(f"Starting Silver job for table: {table_name}")
logger.info(f"Reading Raw data from: {raw_path}")

df = (
    spark.read
    .schema(schema)
    .option("header", "true")
    .option("enforceSchema", "false")
    .option("mode", "FAILFAST")
    .option("delimiter", ",")
    .option("timestampFormat", "yyyy-MM-dd HH:mm:ss")
    .option("multiLine", "true" if table_name == "reviews" else "false")
    .option("escape", '"')
    .csv(raw_path)
)

df = normalize_string_columns(df)

source_df = df.cache()
validate_table_quality(source_df, table_name, logger)
df = source_df

df = apply_silver_transformations(df, table_name)

logger.info(f"Writing Silver data to: {silver_path}")
df.write.mode("overwrite").parquet(silver_path)
source_df.unpersist()

job.commit()
