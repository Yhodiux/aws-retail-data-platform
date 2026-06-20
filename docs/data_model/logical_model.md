# Logical Data Model

The core analytical model uses six Silver datasets. Reviews, geolocation, and category translation are registered for future extensions but are not required by the current Gold jobs.

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--o{ PAYMENTS : receives
    PRODUCTS ||--o{ ORDER_ITEMS : identifies
    SELLERS ||--o{ ORDER_ITEMS : fulfills

    CUSTOMERS {
        string customer_id PK
        string customer_unique_id
        string customer_zip_code_prefix
        string customer_city
        string customer_state
    }

    ORDERS {
        string order_id PK
        string customer_id FK
        string order_status
        timestamp order_purchase_timestamp
    }

    ORDER_ITEMS {
        string order_id PK,FK
        int order_item_id PK
        string product_id FK
        string seller_id FK
        decimal price
        decimal freight_value
    }

    PAYMENTS {
        string order_id PK,FK
        int payment_sequential PK
        string payment_type
        int payment_installments
        decimal payment_value
    }

    PRODUCTS {
        string product_id PK
        string product_category_name
    }

    SELLERS {
        string seller_id PK
        string seller_state
    }
```

## Enforced Silver relationships

- `orders.customer_id -> customers.customer_id`
- `order_items.order_id -> orders.order_id`
- `order_items.product_id -> products.product_id`
- `order_items.seller_id -> sellers.seller_id`
- `payments.order_id -> orders.order_id`

## Gold grains

| Dataset | Grain |
|---|---|
| `sales_by_state` | customer state |
| `sales_by_category` | product category, including `UNKNOWN` |
| `sales_by_payment_type` | payment type |
| `top_customers` | customer unique ID and customer state |
| `top_sellers` | seller ID and seller state |

See [Gold data contracts](../gold-data-contracts.md) for complete column semantics.
