"""Read-only image diagnostics on synthetic local product fixtures."""

from io import StringIO
import json
from unittest.mock import patch

import cloudinary
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.db.models import TextField, Value
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from .models import Product


class ProductImageDiagnosticTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Image diagnostic fixture", price="11.49",
            image="image/upload/v1771237247/fixture.png",
        )

    def diagnose(self, **options):
        output = StringIO()
        with patch("socket.socket.connect", side_effect=AssertionError("No network")), patch("cloudinary.uploader.upload_resource") as upload:
            call_command("diagnose_product_images", stdout=output, **options)
        upload.assert_not_called()
        return json.loads(output.getvalue())

    def test_default_report_is_read_only_with_no_raw_references_or_credentials(self):
        with CaptureQueriesContext(connection) as captured:
            report = self.diagnose()
        for query in captured:
            self.assertNotIn(query["sql"].split()[0].upper(), {"INSERT", "UPDATE", "DELETE", "ALTER", "CREATE", "DROP"})
        self.assertEqual(report["mode"], "READ_ONLY_NO_NETWORK")
        self.assertTrue(report["cloud_name_configured"])
        self.assertTrue(report["storage_cloud_matches_sdk"])
        self.assertEqual(report["products"][0]["status"], "delivery_url_generated")
        self.assertFalse(report["products"][0]["initial_src_is_placeholder"])
        self.assertNotIn("fixture.png", json.dumps(report))
        self.product.refresh_from_db()
        self.assertEqual(self.product.image.version, "1771237247")

    def test_opt_in_public_url_preserves_original_version_without_upload_prefix_duplication(self):
        report = self.diagnose(product_id=self.product.pk, show_public_urls=True)
        self.assertEqual(report["products"][0]["public_delivery_url"],
                         "https://res.cloudinary.com/offline-test/image/upload/v1771237247/fixture.png")

    def test_missing_cloud_is_classified_without_inventing_configuration(self):
        with patch.object(cloudinary.config(), "cloud_name", None):
            report = self.diagnose(show_public_urls=True)
        self.assertFalse(report["cloud_name_configured"])
        self.assertEqual(report["products"][0]["status"], "cloud_name_unavailable")
        self.assertTrue(report["products"][0]["initial_src_is_placeholder"])
        self.assertNotIn("public_delivery_url", report["products"][0])

    def test_configuration_mismatch_is_reported_without_switching_clouds(self):
        with override_settings(CLOUDINARY_STORAGE={"CLOUD_NAME": "different-fixture"}):
            report = self.diagnose(show_public_urls=True)
        self.assertFalse(report["storage_cloud_matches_sdk"])
        self.assertIn("/offline-test/", report["products"][0]["public_delivery_url"])
        self.assertEqual(cloudinary.config().cloud_name, "offline-test")

    def test_missing_or_credential_shaped_references_are_never_printed(self):
        for stored, status in ((None, "no_reference"), ("", "no_reference"),
                               ("cloudinary://private-fixture-key:private-fixture-secret@fixture", "reference_not_renderable")):
            Product.objects.filter(pk=self.product.pk).update(image=Value(stored, output_field=TextField()))
            with self.subTest(status=status):
                report = self.diagnose(show_public_urls=True)
                self.assertEqual(report["products"][0]["status"], status)
                self.assertNotIn("private-fixture", json.dumps(report))
                self.assertNotIn("public_delivery_url", report["products"][0])

    def test_unknown_or_invalid_product_ids_fail_safely(self):
        with self.assertRaises(CommandError):
            self.diagnose(product_id=self.product.pk + 10000)
        for value in (0, -1, True, 9223372036854775808):
            with self.subTest(value=value), self.assertNumQueries(0), self.assertRaises(CommandError):
                self.diagnose(product_id=value)

    def test_signed_delivery_url_is_not_exposed_even_with_opt_in(self):
        with patch.object(cloudinary.config(), "sign_url", True), patch.object(cloudinary.config(), "api_secret", "synthetic-signing-fixture"):
            report = self.diagnose(show_public_urls=True)
        self.assertEqual(report["products"][0]["status"], "delivery_url_generated")
        self.assertNotIn("public_delivery_url", report["products"][0])
        self.assertNotIn("synthetic-signing-fixture", json.dumps(report))
