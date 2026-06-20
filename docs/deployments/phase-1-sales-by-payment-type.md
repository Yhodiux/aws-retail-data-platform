# Phase 1 Deployment — sales_by_payment_type

Status: deferred to final manual AWS deployment phase

This deployment extends `sales_by_payment_type` without removing or renaming existing fields.

## Files to deploy

| Local file | AWS purpose |
|---|---|
| `libs/common.zip` | Shared Gold transformation functions |
| `scripts/gold/build_gold_sales_by_payment_type.py` | Glue Gold job script |
| `scripts/quality/validate_gold_quality.py` | Shared Glue Gold quality job script |
| `sql/queries.sql` | Manual Athena validation |

The final deployment must upload `libs/common.zip` before this job because the DataFrame transformation now lives in the shared library.

## New columns

- `total_payment_records`
- `delivered_orders`
- `delivered_payment_records`
- `delivered_payment_value`
- `delivered_avg_payment_value`
- `delivered_avg_order_payment_value`

## Deployment order

1. Preserve the current S3 versions of the shared library, Gold script, and quality script.
2. Upload `libs/common.zip` to the configured Glue dependency location.
3. Upload and run the `sales_by_payment_type` Gold script.
4. Run the Gold crawler or update the Data Catalog table.
5. Confirm the six new columns with `DESCRIBE olist_gold_db.sales_by_payment_type` in Athena.
6. Upload the final shared quality script only after all planned Gold jobs are deployed and cataloged.
7. Run the Gold quality job and the payment-type checks from `sql/queries.sql`.
8. Run the complete workflow after all final-phase validations pass.

## Reference values

For the local public Olist source snapshot:

| Metric | Expected value |
|---|---:|
| Payment types with delivered orders | 4 |
| `SUM(delivered_payment_records)` | 100,756 |
| `SUM(delivered_orders)` | 98,659 |
| `SUM(delivered_payment_value)` | 15,422,461.77 |

The 98,659 value represents distinct order-payment-type pairs, not global distinct orders. One order can use multiple payment types.

Reference breakdown:

| Payment type | Delivered orders | Payment records | Payment value |
|---|---:|---:|---:|
| boleto | 19,191 | 19,191 | 2,769,932.58 |
| credit_card | 74,304 | 74,586 | 12,101,094.88 |
| debit_card | 1,485 | 1,486 | 208,421.12 |
| voucher | 3,679 | 5,493 | 343,013.19 |

## Success criteria

- Existing columns remain available.
- All six new columns appear in the catalog and Athena.
- Delivered payment records and value reconcile with the source snapshot.
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
