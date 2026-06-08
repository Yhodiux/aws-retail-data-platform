Customers
---------
PK customer_id
customer_unique_id
customer_city
customer_state

        customer_id
             │
             │
             ▼

Orders
------
PK order_id
FK customer_id
order_status
order_purchase_timestamp

        order_id
             │
             │
             ▼

Order_Items
-----------
FK order_id
FK product_id
FK seller_id
price
freight_value

      │               │
      │               │
      ▼               ▼

Products         Sellers
--------         -------
PK product_id    PK seller_id
product_category seller_state

             Orders
                │
                │ order_id
                ▼

Payments
--------
FK order_id
payment_type
payment_value