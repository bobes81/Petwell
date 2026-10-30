"""Offline image-association regressions using temporary synthetic pictures."""

from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.db.models.query import QuerySet
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from PIL import Image

from orders.models import Order, OrderItem
from .catalogue import MAX_SOURCE_BYTES, PHYSICAL_PRODUCT_NAMES
from .models import Product


class ProductImageAssociationTests(TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.manifest_path = self.directory / "private-plan.json"
        self.products = []
        entries = []
        for index, name in enumerate(sorted(PHYSICAL_PRODUCT_NAMES)):
            product = Product.objects.create(
                name=name, price="8.25", description="Existing owner description.",
                image=None if index % 2 else "",
            )
            self.products.append(product)
            filename = f"fixture-{index}.png"
            Image.new("RGB", (8, 8), (index * 20, 10, 30)).save(
                self.directory / filename, format="PNG"
            )
            entries.append({
                "product_id": product.pk,
                "product_name": name,
                "source_file": filename,
                "sha256": sha256((self.directory / filename).read_bytes()).hexdigest(),
                "provenance": "Synthetic local test fixture, not an actual owner asset.",
                "rights_reviewed": True,
                "ai_generated": True,
                "public_id": f"petwell/ai-products/fixture-{index}",
                "version": 1793260800 + index,
                "format": "png",
            })
        self.manifest = {
            "schema_version": 1, "cloud_name": "offline-test", "products": entries,
        }
        # CloudinaryField prepares model-assigned "" as None. Exercise an actual
        # legacy SQL empty string as well as NULL on SQLite and PostgreSQL.
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products_product SET image = %s WHERE id = %s",
                ["", self.products[0].pk],
            )
        self.legacy_pdf = Product.objects.create(
            name="Mindful Pet Journal (PDF)", description="Existing legacy row.",
            price="4.99", image="legacy/pdf-cover",
        )
        self.order = Order.objects.create(
            full_name="Synthetic Owner", email="fixture@example.test",
            address="Synthetic fixture address", total_price="4.99",
        )
        OrderItem.objects.create(
            order=self.order, product=self.legacy_pdf, quantity=1, price="4.99"
        )
        network = patch(
            "socket.socket.connect",
            side_effect=AssertionError("Image association must stay offline."),
        )
        self.network = network.start()
        self.addCleanup(network.stop)
        upload = patch(
            "cloudinary.uploader.upload_resource",
            side_effect=AssertionError("Image association must not upload."),
        )
        self.upload = upload.start()
        self.addCleanup(upload.stop)

    def run_plan(self, *, apply=False, manifest=None, sources_only=False):
        self.manifest_path.write_text(json.dumps(manifest or self.manifest))
        output = StringIO()
        call_command(
            "associate_product_images", str(self.manifest_path),
            images_dir=str(self.directory), apply=apply,
            sources_only=sources_only, stdout=output,
        )
        self.network.assert_not_called()
        self.upload.assert_not_called()
        return output.getvalue()

    def assert_unassigned(self):
        for product in Product.objects.filter(pk__in=[p.pk for p in self.products]):
            self.assertFalse(product.image)

    def pending_draft(self):
        manifest = deepcopy(self.manifest)
        manifest["cloud_name"] = ""
        for entry in manifest["products"]:
            entry.update(
                product_id=None, public_id="", version=None,
                rights_reviewed=False,
            )
        return manifest

    def test_source_only_checks_pending_draft_without_database_or_cloud_access(self):
        draft = self.pending_draft()
        original = deepcopy(draft)
        with self.assertNumQueries(0), patch(
            "products.management.commands.associate_product_images.cloudinary.config",
            side_effect=AssertionError("Source checks must not use provider config."),
        ) as config, patch(
            "products.catalogue.CloudinaryResource",
            side_effect=AssertionError("Source checks must not construct references."),
        ) as resource:
            output = self.run_plan(sources_only=True, manifest=draft)
        config.assert_not_called()
        resource.assert_not_called()
        self.assertIn("SOURCES ONLY: 9 local AI-concept sources validated", output)
        self.assertEqual(output.count("8x8 PNG"), 9)
        self.assertIn("Rights review pending: 9", output)
        self.assertIn("not a ready-to-apply mapping", output)
        self.assertIn("No database queries/writes, uploads or fetches", output)
        self.assertEqual(draft, original)
        self.assertEqual(json.loads(self.manifest_path.read_text()), original)
        self.assert_unassigned()

    def test_source_only_cannot_apply_and_rejects_before_loading_input(self):
        with self.assertNumQueries(0), patch(
            "products.management.commands.associate_product_images.validate_image_plan",
            side_effect=AssertionError("Incompatible flags must fail before input access."),
        ) as validate:
            with self.assertRaisesMessage(CommandError, "cannot be combined"):
                call_command(
                    "associate_product_images", "not-opened.json",
                    images_dir="not-opened", apply=True, sources_only=True,
                )
        validate.assert_not_called()
        self.assert_unassigned()

    def test_pending_draft_remains_invalid_for_normal_dry_run_or_application(self):
        for apply in (False, True):
            with self.subTest(apply=apply), self.assertNumQueries(0):
                with self.assertRaises(CommandError):
                    self.run_plan(apply=apply, manifest=self.pending_draft())
        self.assert_unassigned()

    def test_source_only_rejects_wrong_hash_name_and_corrupt_source(self):
        for key, value in (
            ("sha256", "0" * 64),
            ("product_name", "Mindful Pet Journal (PDF)"),
        ):
            draft = self.pending_draft()
            draft["products"][0][key] = value
            with self.subTest(field=key), self.assertNumQueries(0):
                with self.assertRaises(CommandError):
                    self.run_plan(sources_only=True, manifest=draft)
        contents = b"This is not an image or an owner asset."
        (self.directory / "fixture-0.png").write_bytes(contents)
        draft = self.pending_draft()
        draft["products"][0]["sha256"] = sha256(contents).hexdigest()
        with self.assertNumQueries(0):
            with self.assertRaisesMessage(CommandError, "not a valid matching"):
                self.run_plan(sources_only=True, manifest=draft)
        self.assert_unassigned()

    def test_source_only_still_requires_distinct_sources_and_valid_attestations(self):
        for key, value in (
            ("sha256", self.manifest["products"][0]["sha256"]),
            ("rights_reviewed", "false"),
            ("provenance", ""),
            ("ai_generated", False),
        ):
            draft = self.pending_draft()
            draft["products"][-1][key] = value
            with self.subTest(field=key), self.assertNumQueries(0):
                with self.assertRaises(CommandError):
                    self.run_plan(sources_only=True, manifest=draft)
        self.assert_unassigned()

    def test_default_dry_run_has_no_database_writes_or_provider_actions(self):
        with CaptureQueriesContext(connection) as queries:
            output = self.run_plan()
        self.assertIn("DRY RUN: 9 empty image fields would be filled", output)
        self.assertIn("Remote asset existence, rights and product accuracy are not verified", output)
        for query in queries:
            self.assertNotIn(
                query["sql"].split()[0].upper(),
                {"INSERT", "UPDATE", "DELETE", "ALTER", "CREATE", "DROP"},
            )
        self.assert_unassigned()
        self.assertEqual(Product.objects.count(), 10)

    def test_apply_preserves_existing_data_history_images_and_is_idempotent(self):
        existing = self.products[0]
        Product.objects.filter(pk=existing.pk).update(image="owner/existing-art", is_available=False)
        catalogue = list(Product.objects.order_by("pk").values(
            "pk", "name", "description", "price", "is_available"
        ))
        original_order = list(Order.objects.values())
        original_items = list(OrderItem.objects.values())
        output = self.run_plan(apply=True)
        self.assertIn("Applied: 8 empty image fields filled; 1 existing images preserved", output)
        for product, entry in zip(self.products[1:], self.manifest["products"][1:]):
            product.refresh_from_db()
            self.assertEqual(product.image.public_id, entry["public_id"])
            self.assertEqual(product.image.version, str(entry["version"]))
            self.assertEqual(product.image.format, "png")
            self.assertEqual(product.image.resource_type, "image")
            self.assertEqual(product.image.type, "upload")
        self.assertIn("Applied: 0 empty image fields filled; 9 existing images preserved", self.run_plan(apply=True))
        existing.refresh_from_db()
        self.legacy_pdf.refresh_from_db()
        self.assertEqual(str(existing.image), "owner/existing-art")
        self.assertEqual(str(self.legacy_pdf.image), "legacy/pdf-cover")
        self.assertEqual(list(Product.objects.order_by("pk").values(
            "pk", "name", "description", "price", "is_available"
        )), catalogue)
        self.assertEqual(list(Order.objects.values()), original_order)
        self.assertEqual(list(OrderItem.objects.values()), original_items)

    def test_wrong_final_database_identity_never_partially_assigns_images(self):
        for key, value in (("product_id", 9223372036854775807),
                           ("product_name", "Not an approved physical product")):
            manifest = deepcopy(self.manifest)
            manifest["products"][-1][key] = value
            with self.subTest(field=key), self.assertRaises(CommandError):
                self.run_plan(apply=True, manifest=manifest)
            self.assert_unassigned()
        Product.objects.filter(pk=self.products[-1].pk).update(name="Owner renamed item")
        with self.assertRaisesMessage(CommandError, "ID and exact name do not match"):
            self.run_plan(apply=True)
        self.assert_unassigned()

    def test_changed_row_during_apply_rolls_back_earlier_assignments(self):
        original_update = QuerySet.update
        calls = 0

        def changed_row(query, **values):
            nonlocal calls
            calls += 1
            return 0 if calls == 2 else original_update(query, **values)

        with patch.object(QuerySet, "update", autospec=True, side_effect=changed_row):
            with self.assertRaisesMessage(CommandError, "all associations were rolled back"):
                self.run_plan(apply=True)
        self.assertEqual(calls, 2)
        self.assert_unassigned()

    def test_wrong_cloud_or_disabled_cloud_fails_without_writes(self):
        manifest = deepcopy(self.manifest)
        manifest["cloud_name"] = "a-different-cloud"
        with self.assertRaisesMessage(CommandError, "must match the configured"):
            self.run_plan(apply=True, manifest=manifest)
        with override_settings(CLOUDINARY_STORAGE={"CLOUD_NAME": None}):
            with self.assertRaisesMessage(CommandError, "must match the configured"):
                self.run_plan(apply=True)
        self.assert_unassigned()

    def test_duplicate_ids_sources_or_image_references_are_rejected(self):
        for key in ("product_id", "product_name", "public_id", "sha256"):
            manifest = deepcopy(self.manifest)
            manifest["products"][-1][key] = manifest["products"][0][key]
            with self.subTest(field=key), self.assertRaisesMessage(CommandError, "must be distinct"):
                self.run_plan(apply=True, manifest=manifest)
            self.assert_unassigned()

    def test_placeholder_or_unsafe_reference_values_are_rejected(self):
        variants = [
            ("product_id", None), ("version", None), ("version", True),
            ("rights_reviewed", False), ("ai_generated", False),
            ("provenance", ""), ("sha256", ""), ("format", {}),
            ("public_id", "https://res.cloudinary.com/private-key/image/upload/file.png"),
            ("public_id", "petwell/ai-products/picture.png"),
            ("public_id", "petwell/ai-products/file?secret=do-not-echo"),
        ]
        for key, value in variants:
            manifest = deepcopy(self.manifest)
            manifest["products"][0][key] = value
            with self.subTest(field=key, value_type=type(value).__name__):
                with self.assertRaises(CommandError) as error:
                    self.run_plan(apply=True, manifest=manifest)
                self.assertNotIn("private-key", str(error.exception))
                self.assertNotIn("do-not-echo", str(error.exception))
                self.assert_unassigned()

    def test_sources_cannot_escape_directory_or_use_symlinks(self):
        (self.directory / "linked.png").symlink_to(self.directory / "fixture-0.png")
        for name in ("../fixture-0.png", "/private/file.png", "sub/file.png",
                     "sub\\file.png", "linked.png", "missing.png"):
            manifest = deepcopy(self.manifest)
            manifest["products"][0]["source_file"] = name
            with self.subTest(source=name), self.assertRaises(CommandError):
                self.run_plan(apply=True, manifest=manifest)
            self.assert_unassigned()

    def test_source_hash_size_content_and_declared_format_are_checked(self):
        manifest = deepcopy(self.manifest)
        manifest["products"][0]["sha256"] = "0" * 64
        with self.assertRaisesMessage(CommandError, "SHA-256 does not match"):
            self.run_plan(apply=True, manifest=manifest)
        manifest = deepcopy(self.manifest)
        manifest["products"][0]["format"] = "jpg"
        with self.assertRaisesMessage(CommandError, "not a valid matching"):
            self.run_plan(apply=True, manifest=manifest)
        source = self.directory / "fixture-0.png"
        for contents in (b"Not an image", b"x" * (MAX_SOURCE_BYTES + 1)):
            source.write_bytes(contents)
            manifest = deepcopy(self.manifest)
            manifest["products"][0]["sha256"] = sha256(contents).hexdigest()
            with self.assertRaises(CommandError):
                self.run_plan(apply=True, manifest=manifest)
            self.assert_unassigned()

    def test_pillow_decompression_warning_is_an_error(self):
        with patch.object(Image, "MAX_IMAGE_PIXELS", 40):
            with self.assertRaisesMessage(CommandError, "not a valid matching"):
                self.run_plan(apply=True)
        self.assert_unassigned()

    def test_png_chunk_crc_error_is_a_sanitized_validation_failure(self):
        source = self.directory / "fixture-0.png"
        corrupt = bytearray(source.read_bytes())
        # Alter the IDAT CRC immediately before the final IEND chunk. Pillow
        # opens the header but verify() raises SyntaxError for the damaged CRC.
        corrupt[-16] ^= 1
        source.write_bytes(corrupt)
        manifest = deepcopy(self.manifest)
        manifest["products"][0]["sha256"] = sha256(corrupt).hexdigest()
        with self.assertRaisesMessage(CommandError, "not a valid matching") as error:
            self.run_plan(apply=True, manifest=manifest)
        self.assertNotIn(str(self.directory), str(error.exception))
        self.assert_unassigned()

    def test_matching_jpeg_and_webp_sources_can_be_associated(self):
        manifest = deepcopy(self.manifest)
        for index, (pillow_format, cloudinary_format) in enumerate(
            (("JPEG", "jpg"), ("WEBP", "webp"))
        ):
            entry = manifest["products"][index]
            filename = f"fixture-{index}.{cloudinary_format}"
            path = self.directory / filename
            Image.new("RGB", (8, 8), (100, index * 50, 40)).save(
                path, format=pillow_format
            )
            entry.update(
                source_file=filename, format=cloudinary_format,
                sha256=sha256(path.read_bytes()).hexdigest(),
            )
        self.run_plan(apply=True, manifest=manifest)
        for index, expected in enumerate(("jpg", "webp")):
            self.products[index].refresh_from_db()
            self.assertEqual(self.products[index].image.format, expected)

    def test_malformed_or_ambiguous_json_is_sanitized_and_rejected(self):
        for contents in ('{"private-key":"do-not-echo"',
                         '{"schema_version":1,"schema_version":1}',
                         '[' * 2000 + '0' + ']' * 2000):
            self.manifest_path.write_text(contents)
            with self.assertRaises(CommandError) as error:
                call_command(
                    "associate_product_images", str(self.manifest_path),
                    images_dir=str(self.directory), apply=True,
                )
            self.assertNotIn("private-key", str(error.exception))
            self.assertNotIn("do-not-echo", str(error.exception))
            self.assertNotIn(str(self.directory), str(error.exception))
            self.assert_unassigned()

    def test_nonregular_manifest_is_rejected_before_any_open_can_block(self):
        self.manifest_path.write_text(json.dumps(self.manifest))
        link = self.directory / "linked-manifest.json"
        link.symlink_to(self.manifest_path)
        invalid_paths = [self.directory, link]
        if hasattr(os, "mkfifo"):
            fifo = self.directory / "manifest-fifo"
            os.mkfifo(fifo)
            invalid_paths.append(fifo)
        for path in invalid_paths:
            with self.subTest(kind=path.name):
                # Refuse both the old Path.open and low-level open so this
                # regression cannot hang even if FIFO validation is removed.
                with patch.object(Path, "open", side_effect=AssertionError(
                    "Non-regular manifests must not be opened."
                )), patch("products.catalogue.os.open", side_effect=AssertionError(
                    "Non-regular manifests must not be opened."
                )):
                    with self.assertRaisesMessage(CommandError, "regular, non-symlink") as error:
                        call_command(
                            "associate_product_images", str(path),
                            images_dir=str(self.directory), apply=True,
                        )
                self.assertNotIn(str(self.directory), str(error.exception))
                self.assert_unassigned()

    def test_concept_images_keep_their_identity_without_a_duplicate_card_caption(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertNotContains(response, "AI-generated product illustration")
        self.run_plan(apply=True)
        response = self.client.get(reverse("products:product_list"))
        self.assertNotContains(response, "AI-generated product illustration")
        for product in Product.objects.filter(pk__in=[p.pk for p in self.products]):
            self.assertTrue(product.image_is_ai_illustration)
            self.assertContains(response, f'alt="{product.name}"')
            self.assertContains(response, product.description)
        self.assertFalse(Product.objects.get(pk=self.legacy_pdf.pk).image_is_ai_illustration)

    def test_full_concept_display_is_scoped_to_ai_images(self):
        Product.objects.filter(pk=self.products[0].pk).update(image="owner/existing-art")
        self.run_plan(apply=True)
        response = self.client.get(reverse("products:product_list"))

        class Images(HTMLParser):
            def __init__(self):
                super().__init__()
                self.images = []

            def handle_starttag(self, tag, attrs):
                if tag == "img":
                    self.images.append(dict(attrs))

        parser = Images()
        parser.feed(response.content.decode())
        concepts = [image for image in parser.images
                    if "petwell/ai-products/" in image.get("src", "")]
        ordinary = [image for image in parser.images
                    if "owner/existing-art" in image.get("src", "")]
        self.assertEqual(len(concepts), 8)
        self.assertEqual(len(ordinary), 1)
        self.assertTrue(all("product-concept-image" in image.get("class", "").split()
                            for image in concepts))
        self.assertNotIn("product-concept-image", ordinary[0].get("class", "").split())
        self.assertNotContains(response, "AI-generated product illustration")
