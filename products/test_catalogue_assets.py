"""Keep the supplied concept files and public, incomplete draft consistent."""

import json
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase

from .catalogue import ImageMappingError, PHYSICAL_PRODUCT_NAMES, validate_image_plan


class SuppliedConceptSourceTests(SimpleTestCase):
    def test_original_sources_match_draft_without_operational_identifiers(self):
        directory = settings.BASE_DIR / "docs" / "catalogue"
        manifest = directory / "catalogue-images.DRAFT.json"
        draft = json.loads(manifest.read_text())
        self.assertEqual(draft["cloud_name"], "")
        for entry in draft["products"]:
            self.assertIsNone(entry["product_id"])
            self.assertIsNone(entry["version"])
            self.assertEqual(entry["public_id"], "")
            self.assertIs(entry["rights_reviewed"], False)
            self.assertIs(entry["ai_generated"], True)
        with patch("products.catalogue.CloudinaryResource") as resource:
            cloud, sources = validate_image_plan(
                manifest, directory / "concepts", sources_only=True
            )
        resource.assert_not_called()
        self.assertEqual(cloud, "")
        self.assertEqual({row["product_name"] for row in sources}, PHYSICAL_PRODUCT_NAMES)
        self.assertEqual(len(sources), 9)
        self.assertEqual(len({row["sha256"] for row in sources}), 9)
        self.assertTrue(all(
            (row["width"], row["height"], row["format"]) == (1000, 1000, "png")
            for row in sources
        ))
        with self.assertRaises(ImageMappingError):
            validate_image_plan(manifest, directory / "concepts")
