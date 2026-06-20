# Phase 1 Deployment — sales_by_category

Status: deferred to final manual AWS deployment phase

This deployment extends `sales_by_category` without removing or renaming existing fields.

## Files to deploy

| Local file | AWS purpose |
|---|---|
| `libs/common.zip` | Shared Gold transformation functions |
| `scripts/gold/build_gold_sales_by_category.py` | Glue Gold job script |
| `scripts/quality/validate_gold_quality.py` | Shared Glue Gold quality job script |
| `sql/queries.sql` | Manual Athena validation |

The final deployment must upload `libs/common.zip` before this job because the DataFrame transformation now lives in the shared library.

## New columns

- `delivered_orders`
- `delivered_items`
- `delivered_product_revenue`
- `delivered_freight_value`
- `delivered_avg_item_price`
- `delivered_avg_ticket`

## Deployment order

1. Preserve the current S3 versions of the shared library, Gold script, and quality script.
2. Upload `libs/common.zip` to the configured Glue dependency location.
3. Upload and run the `sales_by_category` Gold script.
4. Run the Gold crawler or update the Data Catalog table using the established procedure.
5. Confirm the six new columns with `DESCRIBE olist_gold_db.sales_by_category` in Athena.
6. After all planned Gold jobs have been deployed and cataloged, upload the final quality script once.
7. Run the Gold quality job.
8. Execute the category checks in `sql/queries.sql`.
9. Run the complete workflow after all final-phase validations pass.

## Reference values

For the local public Olist source snapshot:

| Metric | Expected value |
|---|---:|
| Category rows | 74 |
| `SUM(delivered_items)` | 110,197 |
| `SUM(delivered_orders)` | 97,276 |
| `SUM(delivered_product_revenue)` | 13,221,498.11 |
| `SUM(delivered_freight_value)` | 2,198,275.64 |

The 97,276 value represents distinct order-category pairs, not global distinct orders. One order can contribute to more than one category. Delivered items, revenue, and freight must reconcile with `sales_by_state`.

## Success criteria

- Existing columns remain available.
- All six new columns appear in the catalog and Athena.
- Global delivered item, product-revenue, and freight totals reconcile with `sales_by_state`.
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
