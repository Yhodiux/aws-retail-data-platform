from pyspark.sql.functions import col, trim, upper


def normalize_string_columns(df):
    data_types = dict(df.dtypes)
    for column_name in df.columns:
        if data_types[column_name] == "string":
            df = df.withColumn(column_name, trim(col(column_name)))
    return df


def apply_silver_transformations(df, table_name):
    if table_name == "customers":
        return (
            df
            .withColumn("customer_city", upper(col("customer_city")))
            .withColumn("customer_state", upper(col("customer_state")))
            .dropDuplicates(["customer_id"])
        )

    if table_name == "orders":
        return df.dropDuplicates(["order_id"])

    return df

