from pyspark.sql.functions import (
    coalesce,
    col,
    count,
    lit,
    sum as spark_sum,
    trim,
    when,
)
from pyspark.sql.types import StringType

from common.quality_rules import get_table_quality_rules


class DataQualityError(ValueError):
    """Raised when a dataset violates one or more configured quality rules."""


def _required_condition(df, column_name):
    condition = col(column_name).isNull()
    if isinstance(df.schema[column_name].dataType, StringType):
        condition = condition | (trim(col(column_name)) == "")
    return condition


def _invalid_count(condition, label):
    return coalesce(
        spark_sum(when(condition, 1).otherwise(0)),
        lit(0),
    ).cast("long").alias(label)


def validate_table_quality(df, table_name, logger):
    rules = get_table_quality_rules(table_name)
    validation_expressions = [count(lit(1)).alias("__row_count")]
    validation_labels = []

    for column_name in rules.get("required", []):
        label = f"required:{column_name}"
        validation_labels.append(label)
        validation_expressions.append(
            _invalid_count(_required_condition(df, column_name), label)
        )

    for column_name in rules.get("non_negative", []):
        label = f"non_negative:{column_name}"
        validation_labels.append(label)
        validation_expressions.append(
            _invalid_count(col(column_name) < 0, label)
        )

    for column_name, allowed_values in rules.get("allowed_values", {}).items():
        label = f"allowed_values:{column_name}"
        validation_labels.append(label)
        validation_expressions.append(
            _invalid_count(
                col(column_name).isNotNull()
                & ~col(column_name).isin(sorted(allowed_values)),
                label,
            )
        )

    for column_name, (minimum, maximum) in rules.get("ranges", {}).items():
        label = f"range:{column_name}"
        validation_labels.append(label)
        validation_expressions.append(
            _invalid_count(
                col(column_name).isNotNull()
                & ((col(column_name) < minimum) | (col(column_name) > maximum)),
                label,
            )
        )

    result = df.agg(*validation_expressions).collect()[0].asDict()
    errors = []
    if result["__row_count"] == 0:
        errors.append("table is empty")

    errors.extend([
        f"{label} failed for {result[label]} rows"
        for label in validation_labels
        if result[label] > 0
    ])

    for key_columns in rules.get("unique", []):
        duplicate_key_count = (
            df.groupBy(*key_columns)
            .count()
            .filter(col("count") > 1)
            .count()
        )
        if duplicate_key_count > 0:
            errors.append(
                f"unique:{','.join(key_columns)} failed for "
                f"{duplicate_key_count} duplicate keys"
            )

    if errors:
        raise DataQualityError(
            f"Silver quality validation failed for {table_name}: "
            + " | ".join(errors)
        )

    logger.info(f"Silver quality validation passed for: {table_name}")


def count_orphan_records(
    child_df,
    parent_df,
    child_column,
    parent_column,
):
    parent_keys = parent_df.select(parent_column).dropDuplicates()
    return (
        child_df.select(child_column).alias("child")
        .join(
            parent_keys.alias("parent"),
            col(f"child.{child_column}") == col(f"parent.{parent_column}"),
            "left_anti",
        )
        .count()
    )
