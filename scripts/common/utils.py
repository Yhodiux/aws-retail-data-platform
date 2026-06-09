from pyspark.sql import DataFrame


def log_dataframe_count(df: DataFrame, logger, dataset_name: str) -> None:
    count = df.count()
    logger.info(f"{dataset_name} row count: {count}")


def write_parquet(df: DataFrame, output_path: str, mode: str = "overwrite", partitions: int = 1) -> None:
    (
        df.coalesce(partitions)
        .write
        .mode(mode)
        .parquet(output_path)
    )