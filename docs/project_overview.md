# Olist Retail Data Platform

AWS Data Lakehouse Project

## Architecture

CSV Files
→ S3 Raw
→ Glue Silver ETL
→ S3 Silver
→ Glue Gold Aggregations
→ S3 Gold
→ Glue Catalog
→ Athena
→ Power BI

## Technologies

- Amazon S3
- AWS Glue
- AWS Glue Catalog
- Amazon Athena
- PySpark
- Parquet
- Power BI

## Layers

### Raw
Original Olist datasets

### Silver
Cleaned and standardized datasets

### Gold
Business metrics datasets

- sales_by_state
- sales_by_category
- sales_by_payment_type
- top_sellers
- top_customers