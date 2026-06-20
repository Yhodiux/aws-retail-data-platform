# Data Source

## Dataset

This project uses the public **Brazilian E-Commerce Public Dataset by Olist**, published on Kaggle:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

The source CSV files are not part of this Git repository. They must be downloaded from the publisher and loaded into the Raw S3 layer by the project owner.

## Expected source files

| Source file | Logical dataset | Raw S3 prefix used by the pipeline |
|---|---|---|
| `olist_customers_dataset.csv` | customers | `raw/customers/` |
| `olist_orders_dataset.csv` | orders | `raw/orders/` |
| `olist_order_items_dataset.csv` | order_items | `raw/order_items/` |
| `olist_order_payments_dataset.csv` | payments | `raw/payments/` |
| `olist_products_dataset.csv` | products | `raw/products/` |
| `olist_sellers_dataset.csv` | sellers | `raw/sellers/` |
| `olist_geolocation_dataset.csv` | geolocation | `raw/geolocation/` |
| `olist_order_reviews_dataset.csv` | reviews | `raw/reviews/` |
| `product_category_name_translation.csv` | category translation | `raw/product_category_translation/` |

The current Silver and Gold pipeline primarily consumes customers, orders, order items, payments, products, and sellers. The remaining files are reserved for future extensions.

## Loading Raw data

1. Download the dataset from the publisher.
2. Keep the original CSV content unchanged.
3. Upload each file to the logical Raw prefix shown above.
4. Confirm that each object has a CSV content type where practical.
5. Record the source download date and, when available, a checksum or dataset version.
6. Run the corresponding Silver job with its logical `TABLE_NAME` value.

Example logical mapping:

```text
olist_order_payments_dataset.csv
    -> s3://<project-bucket>/raw/payments/
    -> Glue argument: --TABLE_NAME payments
```

## Data handling rules

- Do not commit the downloaded CSV or ZIP files.
- Do not rename source columns before the Raw layer.
- Treat Raw as immutable source evidence.
- Perform normalization and type conversion in Silver.
- Keep credentials and account-specific identifiers outside the dataset and repository.

