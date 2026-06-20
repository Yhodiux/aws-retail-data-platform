# Gold Data Contracts

This document defines the grain and business meaning of each Gold dataset. Existing fields are retained for backward compatibility. New fields use explicit names and do not change the meaning of legacy fields.

## sales_by_state

Status: implemented locally; pending AWS deployment and validation

Grain: one row per customer state (`customer_state`).

Source datasets:

- `orders`
- `customers`
- `order_items`

| Column | Definition | Compatibility |
|---|---|---|
| `customer_state` | Customer state associated with the order. | Existing |
| `total_orders` | Distinct orders in any status. | Existing |
| `total_items` | Order-item rows associated with orders in any status. | Existing |
| `total_sales` | Sum of item price for orders in any status. | Existing legacy metric |
| `total_freight` | Sum of item freight for orders in any status. | Existing legacy metric |
| `avg_ticket` | `total_sales / total_orders` for orders in any status. | Existing legacy metric |
| `delivered_orders` | Distinct orders whose status is `delivered`. | New |
| `delivered_items` | Order-item rows whose order status is `delivered`. | New |
| `delivered_product_revenue` | Sum of item price for delivered orders. | New |
| `delivered_freight_value` | Sum of item freight for delivered orders. | New |
| `delivered_avg_ticket` | `delivered_product_revenue / delivered_orders`; null when there are no delivered orders. | New |

Reconciliation expectations:

- `delivered_orders <= total_orders`
- `delivered_items <= total_items`
- All count and monetary metrics are non-negative.
- `delivered_avg_ticket` is null only when `delivered_orders` is zero.

Deployment procedure: `docs/deployments/phase-1-sales-by-state.md`.

## sales_by_category

Status: implemented locally; pending final AWS deployment and validation

Grain: one row per product category (`product_category_name`). Missing categories are grouped as `UNKNOWN`.

Source datasets:

- `orders`
- `order_items`
- `products`

| Column | Definition | Compatibility |
|---|---|---|
| `product_category_name` | Product category or `UNKNOWN` when missing. | Existing |
| `total_orders` | Distinct orders in any status containing the category. | Existing |
| `total_items` | Order-item rows in any status for the category. | Existing |
| `total_sales` | Sum of item price for orders in any status. | Existing legacy metric |
| `avg_price` | Average item price for orders in any status. | Existing legacy metric |
| `delivered_orders` | Distinct delivered orders containing the category. | New |
| `delivered_items` | Order-item rows from delivered orders for the category. | New |
| `delivered_product_revenue` | Sum of item price from delivered orders for the category. | New |
| `delivered_freight_value` | Sum of item freight from delivered orders for the category. | New |
| `delivered_avg_item_price` | Average item price from delivered orders for the category. | New |
| `delivered_avg_ticket` | Delivered product revenue divided by distinct delivered orders containing the category. | New |

Reconciliation expectations:

- `delivered_orders <= total_orders` within each category.
- `delivered_items <= total_items` within each category.
- Summing `delivered_orders` across categories is not a global distinct-order count because one order may contain products from multiple categories.
- All count and monetary metrics are non-negative.

Deployment procedure: `docs/deployments/phase-1-sales-by-category.md`.

## sales_by_payment_type

Status: implemented locally; pending final AWS deployment and validation

Grain: one row per payment type (`payment_type`).

Source datasets:

- `orders`
- `payments`

| Column | Definition | Compatibility |
|---|---|---|
| `payment_type` | Payment method associated with the payment record. | Existing |
| `total_orders` | Distinct orders in any status using the payment type. | Existing |
| `total_sales` | Sum of payment value for orders in any status. | Existing legacy metric |
| `avg_payment_value` | Average value per payment record for orders in any status. | Existing |
| `total_payment_records` | Number of payment records in any order status. | New |
| `delivered_orders` | Distinct delivered orders using the payment type. | New |
| `delivered_payment_records` | Number of payment records associated with delivered orders. | New |
| `delivered_payment_value` | Sum of payment value associated with delivered orders. | New |
| `delivered_avg_payment_value` | Average value per payment record associated with delivered orders. | New |
| `delivered_avg_order_payment_value` | Delivered payment value divided by distinct delivered orders using the payment type. | New |

Reconciliation expectations:

- `delivered_orders <= total_orders` within each payment type.
- `delivered_payment_records <= total_payment_records` within each payment type.
- Summing `delivered_orders` across payment types is not necessarily a global distinct-order count because an order can use multiple payment types.
- `delivered_avg_payment_value` is a per-record average; `delivered_avg_order_payment_value` is a per-order average.
- All count and monetary metrics are non-negative.

Deployment procedure: `docs/deployments/phase-1-sales-by-payment-type.md`.

## top_customers

Status: implemented locally; pending final AWS deployment and validation

Grain: one row per customer unique ID and customer state (`customer_unique_id`, `customer_state`). A customer appearing in more than one state can produce more than one row to preserve the existing dataset grain.

Source datasets:

- `customers`
- `orders`
- `payments`

| Column | Definition | Compatibility |
|---|---|---|
| `customer_unique_id` | Stable customer identifier from the Olist source. | Existing |
| `customer_state` | State associated with the order-level customer record. | Existing |
| `total_orders` | Distinct orders in any status. | Existing |
| `total_sales` | Sum of payment value for orders in any status. | Existing legacy metric |
| `avg_ticket` | Legacy total payment value divided by distinct orders in any status. | Existing |
| `total_payment_records` | Number of payment records in any order status. | New |
| `delivered_orders` | Distinct delivered orders for the customer-state row. | New |
| `delivered_payment_records` | Payment records associated with delivered orders. | New |
| `delivered_payment_value` | Sum of payment value associated with delivered orders. | New |
| `delivered_first_purchase_at` | Earliest purchase timestamp among delivered orders. | New |
| `delivered_last_purchase_at` | Latest purchase timestamp among delivered orders. | New |
| `delivered_avg_order_payment_value` | Delivered payment value divided by distinct delivered orders. | New |

Reconciliation expectations:

- `delivered_orders <= total_orders` per customer-state row.
- `delivered_payment_records <= total_payment_records` per customer-state row.
- `delivered_first_purchase_at <= delivered_last_purchase_at` when delivered orders exist.
- Delivered date fields are null when a customer-state row has no delivered orders.
- All count and monetary metrics are non-negative.
- The existing inner join to payments excludes orders without a payment record; the standard source snapshot contains one delivered order in this situation.

Deployment procedure: `docs/deployments/phase-1-top-customers.md`.

## top_sellers

Status: implemented locally; pending final AWS deployment and validation

Grain: one row per seller and seller state (`seller_id`, `seller_state`).

Source datasets:

- `orders`
- `order_items`
- `sellers`

| Column | Definition | Compatibility |
|---|---|---|
| `seller_id` | Seller identifier associated with the order item. | Existing |
| `seller_state` | State from the seller reference dataset. | Existing |
| `total_orders` | Distinct orders in any status containing seller items. | Existing |
| `total_items` | Seller order-item rows from orders in any status. | Existing |
| `total_sales` | Sum of seller item price for orders in any status. | Existing legacy metric |
| `delivered_orders` | Distinct delivered orders containing seller items. | New |
| `delivered_items` | Seller order-item rows from delivered orders. | New |
| `delivered_product_revenue` | Sum of seller item price from delivered orders. | New |
| `delivered_freight_value` | Sum of seller item freight from delivered orders. | New |
| `delivered_avg_item_price` | Average seller item price from delivered orders. | New |
| `delivered_first_sale_at` | Earliest purchase timestamp among delivered seller orders. | New |
| `delivered_last_sale_at` | Latest purchase timestamp among delivered seller orders. | New |
| `delivered_avg_order_product_revenue` | Delivered product revenue divided by distinct delivered seller orders. | New |

Reconciliation expectations:

- `delivered_orders <= total_orders` per seller-state row.
- `delivered_items <= total_items` per seller-state row.
- Summing `delivered_orders` across sellers is not a global distinct-order count because one order can contain items from multiple sellers.
- `delivered_first_sale_at <= delivered_last_sale_at` when delivered orders exist.
- Delivered date fields are null when a seller has no delivered orders.
- All count and monetary metrics are non-negative.

Deployment procedure: `docs/deployments/phase-1-top-sellers.md`.
