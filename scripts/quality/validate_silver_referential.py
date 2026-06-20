import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import current_date, current_timestamp

from common.config import LOGS_BASE_PATH, SILVER_BASE_PATH
from common.data_quality import count_orphan_records
from common.logger import get_logger
from common.quality_rules import SILVER_RELATIONSHIPS


args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

logger = get_logger(args["JOB_NAME"])
logger.info("Starting Silver referential-integrity validation")

results = []

for relationship in SILVER_RELATIONSHIPS:
    child_path = f"{SILVER_BASE_PATH}/{relationship['child_table']}/"
    parent_path = f"{SILVER_BASE_PATH}/{relationship['parent_table']}/"

    child_df = spark.read.parquet(child_path)
    parent_df = spark.read.parquet(parent_path)

    orphan_count = count_orphan_records(
        child_df,
        parent_df,
        relationship["child_column"],
        relationship["parent_column"],
    )

    status = "PASS" if orphan_count == 0 else "FAIL"
    results.append({
        "relationship": relationship["name"],
        "status": status,
        "orphan_count": orphan_count,
    })
    logger.info(
        f"{relationship['name']} status={status} orphan_count={orphan_count}"
    )

results_df = (
    spark.createDataFrame(results)
    .withColumn("execution_timestamp", current_timestamp())
    .withColumn("execution_date", current_date())
)

output_path = f"{LOGS_BASE_PATH}/data-quality/silver/referential/"
(
    results_df.write
    .mode("append")
    .partitionBy("execution_date")
    .parquet(output_path)
)

failed = [result for result in results if result["status"] == "FAIL"]
if failed:
    raise Exception(f"Silver referential-integrity validation failed: {failed}")

logger.info("Silver referential-integrity validation completed successfully")
job.commit()
