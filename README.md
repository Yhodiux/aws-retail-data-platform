# AWS Retail Data Platform

End-to-end AWS Data Lakehouse project built using Amazon S3, AWS Glue, Athena, PySpark and Power BI.

## Architecture

![Architecture](docs/architecture/architecture.png)

## Technologies

- Amazon S3
- AWS Glue
- AWS Glue Catalog
- Amazon Athena
- PySpark
- Power BI
- Parquet

## Data Layers

### Raw Layer
Original Olist ecommerce datasets.

### Silver Layer
Cleaned and standardized datasets stored in Parquet format.

### Gold Layer
Business-oriented datasets optimized for analytics:

- sales_by_state
- sales_by_category
- sales_by_payment_type
- top_sellers
- top_customers

## Analytics

Data is queried through Athena and visualized using Power BI dashboards.

## Dataset

Brazilian E-Commerce Public Dataset by Olist.
