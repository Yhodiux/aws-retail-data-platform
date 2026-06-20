import logging
import unittest
from datetime import datetime
from decimal import Decimal

from pyspark.sql import SparkSession
from pyspark.sql.types import DecimalType, StringType

from common.data_quality import (
    DataQualityError,
    count_orphan_records,
    validate_table_quality,
)
from common.gold_transformations import (
    build_sales_by_category,
    build_sales_by_payment_type,
    build_sales_by_state,
    build_top_customers,
    build_top_sellers,
)
from common.schemas import get_table_schema
from common.silver_transformations import (
    apply_silver_transformations,
    normalize_string_columns,
)


class PySparkPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = (
            SparkSession.builder
            .master("local[2]")
            .appName("aws-retail-data-platform-tests")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .getOrCreate()
        )
        cls.spark.sparkContext.setLogLevel("ERROR")
        cls.logger = logging.getLogger("pipeline-tests")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def _fixtures(self):
        purchase_1 = datetime(2018, 1, 1, 10, 0, 0)
        purchase_2 = datetime(2018, 1, 2, 10, 0, 0)

        customers = self.spark.createDataFrame([
            ("c1", "u1", "01001", "SAO PAULO", "SP"),
        ], [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ])
        orders = self.spark.createDataFrame([
            ("o1", "c1", "delivered", purchase_1),
            ("o2", "c1", "canceled", purchase_2),
        ], [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
        ])
        items = self.spark.createDataFrame([
            ("o1", 1, "p1", "s1", Decimal("100.00"), Decimal("10.00")),
            ("o2", 1, "p2", "s1", Decimal("50.00"), Decimal("5.00")),
        ], [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "price",
            "freight_value",
        ])
        products = self.spark.createDataFrame([
            ("p1", "category_a"),
            ("p2", None),
        ], ["product_id", "product_category_name"])
        payments = self.spark.createDataFrame([
            ("o1", 1, "credit_card", Decimal("80.00")),
            ("o1", 2, "voucher", Decimal("20.00")),
            ("o2", 1, "credit_card", Decimal("50.00")),
        ], [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_value",
        ])
        sellers = self.spark.createDataFrame([
            ("s1", "SP"),
        ], ["seller_id", "seller_state"])
        return customers, orders, items, products, payments, sellers

    def test_explicit_schemas_preserve_business_types(self):
        customers_schema = get_table_schema("customers")
        items_schema = get_table_schema("order_items")

        self.assertIsInstance(
            customers_schema["customer_zip_code_prefix"].dataType,
            StringType,
        )
        self.assertEqual(
            items_schema["price"].dataType,
            DecimalType(12, 2),
        )
        with self.assertRaises(ValueError):
            get_table_schema("unknown_table")

    def test_silver_normalization_trims_and_uppercases_customers(self):
        source = self.spark.createDataFrame([
            (" c1 ", " u1 ", "01001", " sao paulo ", " sp "),
        ], [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ])

        result = apply_silver_transformations(
            normalize_string_columns(source),
            "customers",
        ).collect()[0]

        self.assertEqual(result.customer_id, "c1")
        self.assertEqual(result.customer_unique_id, "u1")
        self.assertEqual(result.customer_city, "SAO PAULO")
        self.assertEqual(result.customer_state, "SP")

    def test_table_quality_accepts_valid_customers(self):
        customers, _, _, _, _, _ = self._fixtures()
        validate_table_quality(customers, "customers", self.logger)

    def test_table_quality_rejects_required_domain_and_unique_violations(self):
        invalid = self.spark.createDataFrame([
            ("", "u1", "01001", "CITY", "XX"),
            ("", "u2", "01002", "CITY", "SP"),
        ], [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ])

        with self.assertRaises(DataQualityError) as context:
            validate_table_quality(invalid, "customers", self.logger)

        message = str(context.exception)
        self.assertIn("required:customer_id", message)
        self.assertIn("allowed_values:customer_state", message)
        self.assertIn("unique:customer_id", message)

    def test_referential_integrity_counts_orphan_rows(self):
        child = self.spark.createDataFrame([
            ("known",),
            ("missing",),
            ("missing",),
        ], ["parent_id"])
        parent = self.spark.createDataFrame([("known",)], ["id"])

        self.assertEqual(
            count_orphan_records(child, parent, "parent_id", "id"),
            2,
        )

    def test_sales_by_state_preserves_legacy_and_adds_delivered_metrics(self):
        customers, orders, items, _, _, _ = self._fixtures()
        row = build_sales_by_state(orders, customers, items).collect()[0]

        self.assertEqual(row.total_orders, 2)
        self.assertEqual(row.total_items, 2)
        self.assertEqual(row.total_sales, Decimal("150.00"))
        self.assertEqual(row.delivered_orders, 1)
        self.assertEqual(row.delivered_items, 1)
        self.assertEqual(row.delivered_product_revenue, Decimal("100.00"))
        self.assertEqual(row.delivered_freight_value, Decimal("10.00"))
        self.assertEqual(row.delivered_avg_ticket, 100.0)

    def test_sales_by_category_handles_unknown_and_delivered_metrics(self):
        _, orders, items, products, _, _ = self._fixtures()
        rows = {
            row.product_category_name: row
            for row in build_sales_by_category(orders, items, products).collect()
        }

        self.assertEqual(set(rows), {"category_a", "UNKNOWN"})
        self.assertEqual(rows["category_a"].delivered_orders, 1)
        self.assertEqual(
            rows["category_a"].delivered_product_revenue,
            Decimal("100.00"),
        )
        self.assertEqual(rows["UNKNOWN"].total_sales, Decimal("50.00"))
        self.assertEqual(rows["UNKNOWN"].delivered_orders, 0)
        self.assertIsNone(rows["UNKNOWN"].delivered_avg_item_price)

    def test_sales_by_payment_type_distinguishes_records_and_orders(self):
        _, orders, _, _, payments, _ = self._fixtures()
        rows = {
            row.payment_type: row
            for row in build_sales_by_payment_type(orders, payments).collect()
        }
        credit = rows["credit_card"]

        self.assertEqual(credit.total_orders, 2)
        self.assertEqual(credit.total_payment_records, 2)
        self.assertEqual(credit.total_sales, Decimal("130.00"))
        self.assertEqual(credit.delivered_orders, 1)
        self.assertEqual(credit.delivered_payment_records, 1)
        self.assertEqual(credit.delivered_payment_value, Decimal("80.00"))
        self.assertEqual(credit.delivered_avg_order_payment_value, 80.0)

    def test_top_customers_tracks_delivered_value_and_dates(self):
        customers, orders, _, _, payments, _ = self._fixtures()
        row = build_top_customers(customers, orders, payments).collect()[0]

        self.assertEqual(row.total_orders, 2)
        self.assertEqual(row.total_sales, Decimal("150.00"))
        self.assertEqual(row.delivered_orders, 1)
        self.assertEqual(row.delivered_payment_records, 2)
        self.assertEqual(row.delivered_payment_value, Decimal("100.00"))
        self.assertEqual(
            row.delivered_first_purchase_at,
            datetime(2018, 1, 1, 10, 0, 0),
        )
        self.assertEqual(
            row.delivered_last_purchase_at,
            datetime(2018, 1, 1, 10, 0, 0),
        )

    def test_top_sellers_tracks_delivered_value_and_dates(self):
        _, orders, items, _, _, sellers = self._fixtures()
        row = build_top_sellers(orders, items, sellers).collect()[0]

        self.assertEqual(row.total_orders, 2)
        self.assertEqual(row.total_items, 2)
        self.assertEqual(row.total_sales, Decimal("150.00"))
        self.assertEqual(row.delivered_orders, 1)
        self.assertEqual(row.delivered_items, 1)
        self.assertEqual(row.delivered_product_revenue, Decimal("100.00"))
        self.assertEqual(row.delivered_avg_order_product_revenue, 100.0)
        self.assertEqual(
            row.delivered_first_sale_at,
            datetime(2018, 1, 1, 10, 0, 0),
        )


if __name__ == "__main__":
    unittest.main()

