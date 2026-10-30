"""Guarded withdrawal tests on synthetic catalogue/history fixtures only."""

from datetime import timedelta
from io import StringIO
import json
from unittest.mock import patch
from uuid import uuid4

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.db.models import TextField, Value
from django.db.models.query import QuerySet
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from orders.models import CheckoutState, Order, OrderItem
from products.models import Product

from .management.commands.review_legacy_pdf import LEGACY_NAME


class LegacyPDFWithdrawalTests(TestCase):
    def setUp(self):
        self.pdf = Product.objects.create(
            name=LEGACY_NAME, description="Synthetic undeliverable legacy fixture.",
            price="4.99", image="image/upload/v100/legacy/pdf.png",
        )
        self.physical = Product.objects.create(
            name="Physical fixture", description="Preserve the physical offer.",
            price="7.25", image="physical/image",
        )
        self.pending = self.order("pending", session="cs_private_fixture")
        self.paid = self.order("paid", payload={"customer_email": "private@example.test"})
        # A second item in the same order must not duplicate order aggregates.
        OrderItem.objects.create(order=self.pending, product=self.pdf, quantity=2, price="3.99")
        self.network = patch(
            "socket.socket.connect",
            side_effect=AssertionError("Withdrawal tests must not use provider networks."),
        )
        self.network_mock = self.network.start()
        self.addCleanup(self.network.stop)
        upload = patch(
            "cloudinary.uploader.upload_resource",
            side_effect=AssertionError("Withdrawal must not upload images."),
        )
        self.upload_mock = upload.start()
        self.addCleanup(upload.stop)

    def order(self, status, session=None, payload=None):
        order = Order.objects.create(
            full_name="Private fixture name", email="private@example.test",
            address="Private fixture address", total_price="4.99", status=status,
            stripe_session_id=session, stripe_checkout_payload=payload or {},
        )
        OrderItem.objects.create(order=order, product=self.pdf, quantity=1, price="4.99")
        return order

    def review(self, **options):
        output = StringIO()
        call_command("review_legacy_pdf", stdout=output, **options)
        self.network_mock.assert_not_called()
        self.upload_mock.assert_not_called()
        return json.loads(output.getvalue())

    def approved(self):
        report = self.review(product_id=self.pdf.pk)
        return {
            "product_id": self.pdf.pk,
            "expected_fingerprint": report["candidates"][0]["snapshot_fingerprint"],
            "confirm_undeliverable": True,
            "checkout_paused": True,
            "orders_reviewed": True,
            "apply": True,
        }

    def assert_no_sql_writes(self, queries):
        for query in queries:
            self.assertNotIn(
                query["sql"].split()[0].upper(),
                {"INSERT", "UPDATE", "DELETE", "ALTER", "DROP", "CREATE"},
            )

    def test_default_exact_name_discovery_has_no_writes_or_sensitive_history(self):
        Product.objects.create(name=LEGACY_NAME.lower(), price="4.99")
        with CaptureQueriesContext(connection) as queries:
            report = self.review()
        self.assert_no_sql_writes(queries)
        self.assertEqual(report["mode"], "DRY_RUN")
        self.assertEqual(report["candidate_count"], 1)
        entry = report["candidates"][0]
        self.assertEqual(entry["product_id"], self.pdf.pk)
        self.assertEqual(entry["history_counts"], {
            "orders": 2, "pending": 1, "paid": 1, "with_session": 1,
            "unmapped_with_payload": 1, "item_rows": 3,
            "purchased_quantity": 4, "active_checkout_leases": 0,
        })
        text = json.dumps(report)
        for sensitive in (self.pending.email, self.pending.full_name,
                          self.pending.address, str(self.pending.public_id),
                          self.pending.stripe_session_id,
                          self.pdf.description, "legacy/pdf.png"):
            self.assertNotIn(sensitive, text)
        self.pdf.refresh_from_db()
        self.assertTrue(self.pdf.is_available)

    def test_duplicate_names_are_reported_without_guessing_a_target(self):
        duplicate = Product.objects.create(name=LEGACY_NAME, price="9.99")
        report = self.review()
        self.assertTrue(report["ambiguous"])
        self.assertEqual(report["candidate_count"], 2)
        self.assertEqual(
            {row["product_id"] for row in report["candidates"]},
            {self.pdf.pk, duplicate.pk},
        )
        self.assertNotEqual(
            report["candidates"][0]["snapshot_fingerprint"],
            report["candidates"][1]["snapshot_fingerprint"],
        )
        with self.assertNumQueries(0), self.assertRaises(CommandError):
            self.review(apply=True)
        options = self.approved()
        self.assertEqual(self.review(**options)["mode"], "APPLIED")
        duplicate.refresh_from_db()
        self.assertTrue(duplicate.is_available)

    def test_application_requires_explicit_identity_fingerprint_and_attestations(self):
        approved = self.approved()
        for key in (
            "product_id", "expected_fingerprint", "confirm_undeliverable",
            "checkout_paused", "orders_reviewed",
        ):
            options = approved.copy()
            options.pop(key)
            with self.subTest(missing=key), self.assertNumQueries(0):
                with self.assertRaises(CommandError):
                    self.review(**options)
        self.pdf.refresh_from_db()
        self.assertTrue(self.pdf.is_available)

    def test_wrong_record_and_stale_fingerprint_are_refused(self):
        approved = self.approved()
        for product_id in (self.physical.pk, self.pdf.pk + 100000):
            options = approved | {"product_id": product_id}
            with self.subTest(product=product_id), self.assertRaises(CommandError):
                self.review(**options)
        for changes in (
            {"description": "Changed since owner review"},
            {"price": "5.99"},
            {"name": "Renamed historical product"},
        ):
            original = {
                "name": self.pdf.name, "description": self.pdf.description,
                "price": self.pdf.price,
            }
            Product.objects.filter(pk=self.pdf.pk).update(**changes)
            with self.subTest(field=next(iter(changes))), self.assertRaises(CommandError):
                self.review(**approved)
            Product.objects.filter(pk=self.pdf.pk).update(**original)
        self.pdf.refresh_from_db()
        self.assertTrue(self.pdf.is_available)

    def test_version_only_image_change_invalidates_review(self):
        approved = self.approved()
        Product.objects.filter(pk=self.pdf.pk).update(
            image="image/upload/v101/legacy/pdf.png"
        )
        with self.assertRaisesMessage(CommandError, "changed since review"):
            self.review(**approved)
        self.pdf.refresh_from_db()
        self.assertTrue(self.pdf.is_available)
        self.assertEqual(self.pdf.image.version, "101")

    def test_withdrawal_preserves_every_other_field_history_and_is_idempotent(self):
        approved = self.approved()
        product_fields = [field.name for field in Product._meta.fields
                          if field.name not in {"image", "is_available"}]
        before_products = list(Product.objects.order_by("pk").values(*product_fields))
        before_orders = list(Order.objects.order_by("pk").values())
        before_items = list(OrderItem.objects.order_by("pk").values())
        image_before = self.review(product_id=self.pdf.pk)["candidates"][0]["image_reference_sha256"]
        applied = self.review(**approved)
        self.assertEqual(applied["mode"], "APPLIED")
        self.assertFalse(applied["candidates"][0]["is_available"])
        self.assertEqual(applied["candidates"][0]["snapshot_fingerprint"], approved["expected_fingerprint"])
        self.assertEqual(applied["candidates"][0]["image_reference_sha256"], image_before)
        with CaptureQueriesContext(connection) as queries:
            again = self.review(**approved)
        self.assert_no_sql_writes(queries)
        self.assertEqual(again["mode"], "ALREADY_WITHDRAWN")
        self.assertEqual(list(Product.objects.order_by("pk").values(*product_fields)), before_products)
        self.assertEqual(list(Order.objects.order_by("pk").values()), before_orders)
        self.assertEqual(list(OrderItem.objects.order_by("pk").values()), before_items)
        self.physical.refresh_from_db()
        self.assertTrue(self.physical.is_available)

    def test_active_checkout_lease_blocks_first_withdrawal(self):
        state = CheckoutState.objects.create(
            session_digest="a" * 64, active_order=self.pending,
            processing_token=uuid4(),
            processing_until=timezone.now() + timedelta(seconds=120),
        )
        with self.assertRaisesMessage(CommandError, "active checkout lease"):
            self.review(**self.approved())
        state.refresh_from_db()
        self.assertIsNotNone(state.processing_token)
        self.pdf.refresh_from_db()
        self.assertTrue(self.pdf.is_available)

    def test_empty_image_variants_can_be_withdrawn_but_not_swapped_after_review(self):
        for stored_image in (None, ""):
            with self.subTest(image=stored_image):
                Product.objects.filter(pk=self.pdf.pk).update(
                    image=Value(stored_image, output_field=TextField()),
                    is_available=True,
                )
                approved = self.approved()
                self.assertEqual(self.review(**approved)["mode"], "APPLIED")
                self.assertEqual(self.review(**approved)["mode"], "ALREADY_WITHDRAWN")
        Product.objects.filter(pk=self.pdf.pk).update(
            image=Value(None, output_field=TextField()), is_available=True,
        )
        approved = self.approved()
        Product.objects.filter(pk=self.pdf.pk).update(
            image=Value("", output_field=TextField()),
        )
        with self.assertRaisesMessage(CommandError, "changed since review"):
            self.review(**approved)
        self.pdf.refresh_from_db()
        self.assertTrue(self.pdf.is_available)

    def test_conditional_update_conflict_is_refused_without_other_changes(self):
        approved = self.approved()
        with patch.object(QuerySet, "update", return_value=0):
            with self.assertRaisesMessage(CommandError, "changed during application"):
                self.review(**approved)
        self.pdf.refresh_from_db()
        self.assertTrue(self.pdf.is_available)

    def test_bad_fingerprint_or_id_rejected_before_database_access(self):
        for options in (
            {"product_id": 0}, {"product_id": True},
            {"product_id": 9223372036854775808},
            {"expected_fingerprint": "not-a-fingerprint"},
        ):
            with self.subTest(option=next(iter(options))), self.assertNumQueries(0):
                with self.assertRaises(CommandError):
                    self.review(**options)

    def test_no_matching_offer_returns_empty_read_only_report(self):
        Product.objects.filter(pk=self.pdf.pk).update(name="Verified future download")
        with CaptureQueriesContext(connection) as queries:
            report = self.review()
        self.assertEqual(report["candidate_count"], 0)
        self.assertEqual(report["mode"], "DRY_RUN")
        self.assert_no_sql_writes(queries)
