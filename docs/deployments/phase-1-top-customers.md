# Phase 1 Deployment — top_customers

Status: deferred to final manual AWS deployment phase

This deployment extends `top_customers` without removing or renaming existing fields.

## Files to deploy

| Local file | AWS purpose |
|---|---|
| `libs/common.zip` | Shared Gold transformation functions |
| `scripts/gold/build_gold_top_customers.py` | Glue Gold job script |
| `scripts/quality/validate_gold_quality.py` | Shared Glue Gold quality job script |
| `sql/queries.sql` | Manual Athena validation |

The final deployment must upload `libs/common.zip` before this job because the DataFrame transformation now lives in the shared library.

## New columns

- `total_payment_records`
- `delivered_orders`
- `delivered_payment_records`
- `delivered_payment_value`
- `delivered_first_purchase_at`
- `delivered_last_purchase_at`
- `delivered_avg_order_payment_value`

## Deployment order

1. Preserve the current S3 versions of the shared library, Gold script, and quality script.
2. Upload `libs/common.zip` to the configured Glue dependency location.
3. Upload and run the `top_customers` Gold script.
4. Run the Gold crawler or update the Data Catalog table.
5. Confirm the seven new columns with `DESCRIBE olist_gold_db.top_customers` in Athena.
6. Upload the final shared quality script only after every planned Gold job is deployed and cataloged.
7. Run the Gold quality job and the customer checks from `sql/queries.sql`.
8. Run the complete workflow after all final-phase validations pass.

## Reference values

For the local public Olist source snapshot:

| Metric | Expected value |
|---|---:|
| Customer-state rows with delivered orders | 93,395 |
| `SUM(delivered_orders)` | 96,477 |
| `SUM(delivered_payment_records)` | 100,756 |
| `SUM(delivered_payment_value)` | 15,422,461.77 |
| Earliest delivered purchase | 2016-10-03 09:44:50 |
| Latest delivered purchase | 2018-08-29 15:00:37 |

The source contains 96,478 delivered orders, but one has no matching payment record. Because `top_customers` intentionally retains its existing inner join to payments, 96,477 delivered orders are represented. Payment records and value must reconcile with `sales_by_payment_type`.

## Success criteria

- Existing columns remain available.
- All seven new columns appear in the catalog and Athena.
- Delivered totals reconcile with the source snapshot.
- Delivered date ranges are valid.
- The invalid-row query returns zero rows.
- The final Gold quality job and complete workflow succeed.

## Rollback

Restore the previous Gold script, regenerate its output, refresh the Data Catalog, and restore the previous shared quality script if the consolidated deployment fails.

## Deployment result

```text
Date:
Environment:
Git commit/release:
Gold Glue run ID:
Gold crawler run:
Quality Glue run ID:
Athena validation result:
Result: PENDING
Notes:
```
