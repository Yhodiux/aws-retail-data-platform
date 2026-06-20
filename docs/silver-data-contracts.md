# Silver Data Contracts

The Silver CSV reader uses explicit PySpark schemas from `scripts/common/schemas.py`. Schema inference is disabled so a source sample cannot silently change column types between runs.

## Reader rules

- Only registered logical `TABLE_NAME` values are accepted.
- CSV headers must match the registered schema.
- Malformed values fail the job through CSV `FAILFAST` mode.
- Timestamps use `yyyy-MM-dd HH:mm:ss`.
- ZIP-code prefixes remain strings to preserve leading zeroes.
- Financial values use `decimal(12,2)` instead of binary floating point.
- Review CSV input enables multiline parsing for quoted comments.
- Raw and Silver paths come from the shared project configuration.

## Registered schemas

### customers

| Column | Type | Required |
|---|---|---|
| `customer_id` | string | Yes |
| `customer_unique_id` | string | Yes |
| `customer_zip_code_prefix` | string | No |
| `customer_city` | string | No |
| `customer_state` | string | No |

### orders

| Column | Type | Required |
|---|---|---|
| `order_id` | string | Yes |
| `customer_id` | string | Yes |
| `order_status` | string | No |
| `order_purchase_timestamp` | timestamp | No |
| `order_approved_at` | timestamp | No |
| `order_delivered_carrier_date` | timestamp | No |
| `order_delivered_customer_date` | timestamp | No |
| `order_estimated_delivery_date` | timestamp | No |

### order_items

| Column | Type | Required |
|---|---|---|
| `order_id` | string | Yes |
| `order_item_id` | integer | Yes |
| `product_id` | string | Yes |
| `seller_id` | string | Yes |
| `shipping_limit_date` | timestamp | No |
| `price` | decimal(12,2) | No |
| `freight_value` | decimal(12,2) | No |

### payments

| Column | Type | Required |
|---|---|---|
| `order_id` | string | Yes |
| `payment_sequential` | integer | Yes |
| `payment_type` | string | No |
| `payment_installments` | integer | No |
| `payment_value` | decimal(12,2) | No |

### products

| Column | Type | Required |
|---|---|---|
| `product_id` | string | Yes |
| `product_category_name` | string | No |
| `product_name_lenght` | integer | No |
| `product_description_lenght` | integer | No |
| `product_photos_qty` | integer | No |
| `product_weight_g` | integer | No |
| `product_length_cm` | integer | No |
| `product_height_cm` | integer | No |
| `product_width_cm` | integer | No |

The source spelling `lenght` is intentionally preserved because Silver remains compatible with the public Olist columns.

### sellers

| Column | Type | Required |
|---|---|---|
| `seller_id` | string | Yes |
| `seller_zip_code_prefix` | string | No |
| `seller_city` | string | No |
| `seller_state` | string | No |

### geolocation

| Column | Type | Required |
|---|---|---|
| `geolocation_zip_code_prefix` | string | No |
| `geolocation_lat` | double | No |
| `geolocation_lng` | double | No |
| `geolocation_city` | string | No |
| `geolocation_state` | string | No |

### reviews

| Column | Type | Required |
|---|---|---|
| `review_id` | string | Yes |
| `order_id` | string | Yes |
| `review_score` | integer | No |
| `review_comment_title` | string | No |
| `review_comment_message` | string | No |
| `review_creation_date` | timestamp | No |
| `review_answer_timestamp` | timestamp | No |

### product_category_translation

| Column | Type | Required |
|---|---|---|
| `product_category_name` | string | Yes |
| `product_category_name_english` | string | No |

## Source validation baseline

All registered headers and data types were validated against the complete local public Olist snapshot on 2026-06-19:

| Logical dataset | Source rows | Result |
|---|---:|---|
| customers | 99,441 | PASS |
| orders | 99,441 | PASS |
| order_items | 112,650 | PASS |
| payments | 103,886 | PASS |
| products | 32,951 | PASS |
| sellers | 3,095 | PASS |
| geolocation | 1,000,163 | PASS |
| reviews | 99,224 | PASS |
| product_category_translation | 71 | PASS |

This baseline validates the source files independently of Spark. Glue runtime validation remains deferred to the final AWS phase.

## Table-level quality controls

The generic Silver job validates each cached DataFrame before applying compatibility transformations or writing Parquet. A violation raises `DataQualityError` and prevents the Silver output from being overwritten.

Configured controls include:

- Non-empty datasets.
- Required values, including blank-string detection.
- Unique primary or composite business keys.
- Non-negative financial, quantity, and dimensional values.
- Allowed order statuses, payment types, and Brazilian state codes.
- Latitude, longitude, and review-score ranges.

The centralized rules are stored in `scripts/common/quality_rules.py`; execution logic is stored in `scripts/common/data_quality.py`.

## Referential-integrity controls

`scripts/quality/validate_silver_referential.py` runs after all core Silver datasets are available and checks:

| Child relationship | Parent relationship |
|---|---|
| `orders.customer_id` | `customers.customer_id` |
| `order_items.order_id` | `orders.order_id` |
| `order_items.product_id` | `products.product_id` |
| `order_items.seller_id` | `sellers.seller_id` |
| `payments.order_id` | `orders.order_id` |

Results are appended as date-partitioned Parquet audit records under `logs/data-quality/silver/referential/`. Any orphan record fails the job after preserving the validation result.

The complete local Olist snapshot has zero violations for the configured table-level rules and zero orphan records for all five relationships.
