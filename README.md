# AWS Retail Data Platform

End-to-end AWS Data Lakehouse project built using Amazon S3, AWS Glue, Athena, PySpark and Power BI.

---

## Project Overview

This project implements a modern Data Lakehouse architecture using AWS services to process and analyze the Olist Brazilian E-Commerce Dataset.

The solution follows a multi-layer architecture:

```text
Raw → Silver → Gold → Analytics
```

The platform ingests raw ecommerce data, standardizes and cleans it through ETL processes, generates business-oriented datasets, and exposes them for analytics through Athena and Power BI.

---

## Architecture

![Architecture](docs/architecture/architecture.png)

### Data Flow

```text
CSV Files
    ↓
S3 Raw
    ↓
AWS Glue ETL
    ↓
S3 Silver
    ↓
AWS Glue Aggregations
    ↓
S3 Gold
    ↓
Glue Catalog
    ↓
Athena
    ↓
Power BI
```

---

## AWS Services Used

| Service | Purpose |
|----------|----------|
| Amazon S3 | Data Lake Storage |
| AWS Glue | ETL Processing |
| AWS Glue Catalog | Metadata Management |
| Amazon Athena | Serverless SQL Analytics |
| IAM | Security and Access Control |

---

## Technologies

- Python
- PySpark
- SQL
- Parquet
- Amazon S3
- AWS Glue
- AWS Athena
- Power BI
- GitHub

---

# Data Layers

## Raw Layer

Stores original source files.

Datasets:

- customers
- orders
- order_items
- products
- payments
- sellers

Storage:

```text
s3://olist-data-engineering-otto/raw/
```

---

## Silver Layer

Standardized and cleansed datasets.

Main transformations:

- Data type standardization
- Null handling
- Data quality validation
- Column normalization
- Parquet optimization

Storage:

```text
s3://olist-data-engineering-otto/silver/
```

---

## Gold Layer

Business-oriented aggregated datasets optimized for analytics.

### sales_by_state

Sales metrics aggregated by customer state.

Columns:

- customer_state
- total_orders
- total_items
- total_sales
- total_freight
- avg_ticket

---

### sales_by_category

Sales metrics aggregated by product category.

Columns:

- product_category_name
- total_orders
- total_items
- total_sales
- avg_price

---

### sales_by_payment_type

Sales metrics aggregated by payment method.

Columns:

- payment_type
- total_orders
- total_sales
- avg_payment_value

---

### top_sellers

Top performing sellers.

Columns:

- seller_id
- seller_state
- total_orders
- total_items
- total_sales

---

### top_customers

Top customers by revenue.

Columns:

- customer_unique_id
- customer_state
- total_orders
- total_sales
- avg_ticket

Storage:

```text
s3://olist-data-engineering-otto/gold/
```

---

# Athena Queries

Athena is used as the analytical query layer.

Example:

```sql
SELECT *
FROM sales_by_state
ORDER BY total_sales DESC;
```

Query scripts:

```text
sql/queries.sql
```

---

# Power BI Dashboard

The Gold layer datasets are consumed by Power BI for reporting and visualization.

Examples:

- Sales by State
- Sales by Category
- Sales by Payment Type
- Top Sellers
- Top Customers

---

# Project Structure

```text
aws-retail-data-platform
│
├── docs
│   ├── architecture
│   │   └── architecture.png
│   └── project_overview.md
│
├── scripts
│   ├── silver
│   └── gold
│
├── sql
│   └── queries.sql
│
├── powerbi
│   └── dashboard.pbix
│
└── README.md
```

---

# Key Data Engineering Concepts Demonstrated

- Data Lake Architecture
- Lakehouse Architecture
- ETL Pipelines
- PySpark Transformations
- Data Quality Validation
- Data Aggregation
- Parquet Optimization
- AWS Glue Catalog
- Athena Analytics
- Business Metrics Modeling

---

# Future Improvements

- AWS Glue Workflow orchestration
- Event-driven ingestion
- AWS Step Functions
- CI/CD with GitHub Actions
- AWS CodePipeline
- Amazon QuickSight integration
- Data Quality Framework
- Infrastructure as Code (Terraform)

---

# Dataset

Brazilian E-Commerce Public Dataset by Olist.

Source:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

---

# Author

Otto Yhoda Alvarez Devars

Senior Data Engineer | Data Governance | PySpark | AWS | Azure | Snowflake
