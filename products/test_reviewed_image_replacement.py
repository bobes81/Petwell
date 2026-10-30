"""Offline rehearsal of owner-approved image-only replacement; synthetic data."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from django.db import connection
from django.db.models import TextField
from django.db.models.functions import Cast
from django.db.models.query import QuerySet
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from PIL import Image

from orders.models import Order, OrderItem
from products.catalogue import ImageMappingError, PHYSICAL_PRODUCT_NAMES
from products.models import Product
from scripts.reviewed_catalogue_images import review, snapshot


class ReviewedImageReplacementTests(TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.manifest_file = self.directory / "manifest.json"
        self.guard_file = self.directory / "guard.json"
        self.products = []
        entries = []
        for i, name in enumerate(sorted(PHYSICAL_PRODUCT_NAMES)):
            product = Product.objects.create(name=name, price="11.49", description="Preserve synthetic original.",
                                             is_available=bool(i % 2), image=f"image/upload/v100/original-{i}.png")
            self.products.append(product)
            filename = f"synthetic-{i}.png"
            Image.new("RGB", (8, 8), (i * 20, 25, 40)).save(self.directory / filename)
            entries.append({"product_id": product.pk, "product_name": name, "source_file": filename,
                            "sha256": sha256((self.directory / filename).read_bytes()).hexdigest(),
                            "provenance": "Synthetic offline fixture only, not an actual uploaded asset.",
                            "rights_reviewed": True, "ai_generated": True,
                            "public_id": f"petwell/ai-products/synthetic-{i}", "version": 200 + i, "format": "png"})
        self.pdf = Product.objects.create(name="Mindful Pet Journal (PDF)", price="4.99", image="legacy/pdf-original")
        order = Order.objects.create(full_name="Synthetic fixture", email="fixture@example.test", address="Synthetic only", total_price="11.49")
        OrderItem.objects.create(order=order, product=self.products[0], price="11.49", quantity=1)
        self.manifest = {"schema_version": 1, "cloud_name": "offline-test", "products": entries}
        self.guard = snapshot()
        for row in self.guard["products"]:
            row["replace_approved"] = True
        self.network = patch("socket.socket.connect", side_effect=AssertionError("No provider network"))
        self.network_mock = self.network.start()
        self.addCleanup(self.network.stop)
        self.upload = patch("cloudinary.uploader.upload_resource", side_effect=AssertionError("No upload"))
        self.upload_mock = self.upload.start()
        self.addCleanup(self.upload.stop)

    def execute(self, *, apply=False, guard=None):
        self.manifest_file.write_text(json.dumps(self.manifest))
        self.guard_file.write_text(json.dumps(self.guard if guard is None else guard))
        result = review(self.manifest_file, self.guard_file, self.directory, apply=apply)
        self.network_mock.assert_not_called()
        self.upload_mock.assert_not_called()
        return result

    def image_references(self):
        return list(Product.objects.annotate(raw_image=Cast("image", output_field=TextField())).order_by("pk").values_list("raw_image", flat=True))

    def test_snapshot_is_read_only_unapproved_and_excludes_pdf(self):
        with CaptureQueriesContext(connection) as queries:
            result = snapshot()
        self.assertEqual(len(result["products"]), 9)
        self.assertEqual({r["product_name"] for r in result["products"]}, PHYSICAL_PRODUCT_NAMES)
        self.assertTrue(all(r["replace_approved"] is False for r in result["products"]))
        for q in queries:
            self.assertNotIn(q["sql"].split()[0].upper(), {"INSERT", "UPDATE", "DELETE"})

    def test_review_is_default_dry_run_without_sql_writes(self):
        before = self.image_references()
        with CaptureQueriesContext(connection) as queries:
            result = self.execute()
        self.assertEqual(result["mode"], "DRY_RUN")
        self.assertEqual(result["images_would_change"], 9)
        for q in queries:
            self.assertNotIn(q["sql"].split()[0].upper(), {"INSERT", "UPDATE", "DELETE"})
        self.assertEqual(self.image_references(), before)

    def test_apply_preserves_all_other_fields_orders_items_pdf_and_sources(self):
        columns = [f.name for f in Product._meta.fields if f.name != "image"]
        products = list(Product.objects.order_by("pk").values(*columns))
        orders = list(Order.objects.values())
        items = list(OrderItem.objects.values())
        files = {p.name: p.read_bytes() for p in self.directory.glob("*.png")}
        result = self.execute(apply=True)
        self.assertEqual(result["images_changed"], 9)
        self.assertEqual(list(Product.objects.order_by("pk").values(*columns)), products)
        self.assertEqual(list(Order.objects.values()), orders)
        self.assertEqual(list(OrderItem.objects.values()), items)
        self.pdf.refresh_from_db()
        self.assertEqual(str(self.pdf.image), "legacy/pdf-original")
        self.assertEqual({p.name: p.read_bytes() for p in self.directory.glob("*.png")}, files)
        for product in self.products:
            product.refresh_from_db()
            self.assertTrue(product.image_is_ai_illustration)

    def test_repeated_application_has_no_update(self):
        self.execute(apply=True)
        with CaptureQueriesContext(connection) as queries:
            result = self.execute(apply=True)
        self.assertEqual(result["images_changed"], 0)
        self.assertEqual(result["already_matching"], 9)
        self.assertFalse(any(q["sql"].lstrip().upper().startswith("UPDATE") for q in queries))

    def test_version_only_stale_reference_refuses_entire_batch(self):
        original = self.products[0].image
        Product.objects.filter(pk=self.products[0].pk).update(image=original.replace("/v100/", "/v101/"))
        before = self.image_references()
        with self.assertRaisesMessage(ImageMappingError, "changed since review"):
            self.execute(apply=True)
        self.assertEqual(self.image_references(), before)

    def test_unapproved_snapshot_cannot_apply(self):
        before = self.image_references()
        with self.assertRaisesMessage(ImageMappingError, "No product replacements"):
            self.execute(apply=True, guard=snapshot())
        self.assertEqual(self.image_references(), before)

    def test_one_approved_smoke_change_then_remaining_eight_is_idempotent(self):
        guard = snapshot()
        guard["products"][0]["replace_approved"] = True
        before = self.image_references()
        result = self.execute(apply=True, guard=guard)
        self.assertEqual((result["images_changed"], result["unapproved_preserved"]), (1, 8))
        self.assertEqual(self.image_references()[1:], before[1:])
        result = self.execute(apply=True)
        self.assertEqual((result["images_changed"], result["already_matching"]), (8, 1))

    def test_identity_approval_and_guard_shape_must_be_explicit(self):
        for key, value in (("product_id", self.pdf.pk), ("product_name", self.pdf.name),
                           ("replace_approved", "yes"), ("expected_image_reference", "")):
            guard = deepcopy(self.guard)
            guard["products"][0][key] = value
            with self.subTest(field=key), self.assertRaises(ImageMappingError):
                self.execute(apply=True, guard=guard)

    def test_mid_batch_conditional_conflict_rolls_back_first_update(self):
        before = self.image_references()
        original = QuerySet.update
        calls = 0
        def conflict(query, **fields):
            nonlocal calls
            calls += 1
            return 0 if calls == 2 else original(query, **fields)
        with patch.object(QuerySet, "update", new=conflict), self.assertRaisesMessage(ImageMappingError, "rolled back"):
            self.execute(apply=True)
        self.assertEqual(calls, 2)
        self.assertEqual(self.image_references(), before)

    def test_duplicate_guard_keys_or_cloud_mismatch_refuse_without_queries(self):
        self.manifest_file.write_text(json.dumps(self.manifest))
        self.guard_file.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertNumQueries(0), self.assertRaises(ImageMappingError):
            review(self.manifest_file, self.guard_file, self.directory, apply=True)
        with override_settings(CLOUDINARY_STORAGE={"CLOUD_NAME": "wrong-fixture"}):
            with self.assertNumQueries(0), self.assertRaises(ImageMappingError):
                self.execute(apply=True)
        guard = deepcopy(self.guard)
        guard["database_fingerprint"] = "0" * 64
        with self.assertNumQueries(0), self.assertRaises(ImageMappingError):
            self.execute(apply=True, guard=guard)

    def test_renamed_or_duplicate_physical_product_requires_new_review(self):
        Product.objects.filter(pk=self.products[0].pk).update(name="Renamed synthetic fixture")
        before = self.image_references()
        with self.assertRaises(ImageMappingError):
            self.execute(apply=True)
        self.assertEqual(self.image_references(), before)
        Product.objects.filter(pk=self.products[0].pk).update(name=self.products[0].name)
        Product.objects.create(name=self.products[0].name, price="1.00", image="duplicate-fixture")
        with self.assertRaises(ImageMappingError):
            snapshot()
