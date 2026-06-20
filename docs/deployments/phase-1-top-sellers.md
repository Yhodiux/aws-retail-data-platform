# Phase 1 Deployment — top_sellers

Status: deferred to final manual AWS deployment phase

This deployment extends `top_sellers` without removing or renaming existing fields.

## Files to deploy

| Local file | AWS purpose |
|---|---|
| `libs/common.zip` | Shared Gold transformation functions |
| `scripts/gold/build_gold_top_sellers.py` | Glue Gold job script |
| `scripts/quality/validate_gold_quality.py` | Shared Glue Gold quality job script |
| `sql/queries.sql` | Manual Athena validation |

The final deployment must upload `libs/common.zip` before this job because the DataFrame transformation now lives in the shared library.

## New columns

- `delivered_orders`
- `delivered_items`
- `delivered_product_revenue`
- `delivered_freight_value`
- `delivered_avg_item_price`
- `delivered_first_sale_at`
- `delivered_last_sale_at`
- `delivered_avg_order_product_revenue`

## Deployment order

1. Preserve the current S3 versions of the shared library, Gold script, and quality script.
2. Upload `libs/common.zip` to the configured Glue dependency location.
3. Upload and run the `top_sellers` Gold script.
4. Run the Gold crawler or update the Data Catalog table.
5. Confirm the eight new columns with `DESCRIBE olist_gold_db.top_sellers` in Athena.
6. Upload the final shared quality script only after every planned Gold job is deployed and cataloged.
7. Run the Gold quality job and the seller checks from `sql/queries.sql`.
8. Run the complete workflow after all final-phase validations pass.

## Reference values

For the local public Olist source snapshot:

| Metric | Expected value |
|---|---:|
| Seller-state rows with delivered orders | 2,970 |
| `SUM(delivered_orders)` | 97,819 |
| `SUM(delivered_items)` | 110,197 |
| `SUM(delivered_product_revenue)` | 13,221,498.11 |
| `SUM(delivered_freight_value)` | 2,198,275.64 |
| Earliest delivered sale | 2016-09-15 12:16:38 |
| Latest delivered sale | 2018-08-29 15:00:37 |

The 97,819 value represents distinct order-seller pairs, not global distinct orders. One order can contain products from multiple sellers. Delivered items, revenue, and freight must reconcile with `sales_by_state` and `sales_by_category`.

## Success criteria

- Existing columns remain available.
- All eight new columns appear in the catalog and Athena.
- Delivered totals and seller date ranges reconcile with the source snapshot.
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
