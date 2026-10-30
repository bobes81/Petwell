"""Offline media-rendering regressions; no provider or production access."""

from html.parser import HTMLParser
from unittest.mock import patch

import cloudinary
from cloudinary.models import CloudinaryField
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from products.models import Product

from .media import image_url


REFERENCE = "image/upload/v1771237247/fixture-product.png"
EXPECTED = "https://res.cloudinary.com/offline-test/image/upload/v1771237247/fixture-product.png"
PLACEHOLDER = "/static/images/placeholder.svg"


class ImageURLTests(SimpleTestCase):
    def test_stored_string_and_sdk_resource_produce_same_versioned_https_url(self):
        resource = CloudinaryField("image").to_python(REFERENCE)
        with patch("socket.socket.connect", side_effect=AssertionError("Offline only")):
            self.assertEqual(image_url(resource), EXPECTED)
            self.assertEqual(image_url(REFERENCE), EXPECTED)
            rendered = Template("{% load petwell_media %}{{ image|image_url }}").render(
                Context({"image": REFERENCE})
            )
        self.assertEqual(rendered, EXPECTED)
        self.assertEqual(resource.version, "1771237247")
        self.assertEqual(resource.get_prep_value(), REFERENCE)

    def test_bare_public_ids_and_versioned_folders_use_sdk_rules(self):
        for value, suffix in (
            ("fixture.png", "/image/upload/fixture.png"),
            ("image/upload/v12/folder/fixture.webp", "/image/upload/v12/folder/fixture.webp"),
        ):
            with self.subTest(value=value):
                self.assertEqual(image_url(value), "https://res.cloudinary.com/offline-test" + suffix)

    def test_missing_cloud_configuration_does_not_invent_a_cloud_or_url(self):
        with patch.object(cloudinary.config(), "cloud_name", None):
            for value in (REFERENCE, CloudinaryField("image").to_python(REFERENCE)):
                with self.subTest(kind=type(value).__name__):
                    self.assertEqual(image_url(value), PLACEHOLDER)

    def test_empty_unsafe_and_malformed_strings_use_local_fallback(self):
        for value in (None, False, "", " ", "/media/file.png", "//example.test/file.png",
                      "cloudinary://fixture-key:fixture-secret@fixture-cloud",
                      "javascript:alert(1)", "https://example.test/file.png",
                      "file.png?token=private", "file.png#fragment", "bad\nreference"):
            with self.subTest(kind=type(value).__name__):
                self.assertEqual(image_url(value), PLACEHOLDER)

    def test_resource_cannot_override_https_and_options_are_not_mutated(self):
        resource = CloudinaryField("image").to_python(REFERENCE)
        resource.url_options = {"secure": False, "width": 80, "crop": "scale"}
        options = resource.url_options.copy()
        url = image_url(resource)
        self.assertTrue(url.startswith("https://res.cloudinary.com/"))
        self.assertIn("c_scale,w_80", url)
        self.assertEqual(resource.url_options, options)

    def test_url_shaped_resource_does_not_emit_an_unsafe_url(self):
        for source in ("http://example.test/private", "https://example.test/private",
                       "cloudinary://private-fixture-key:private-fixture-secret@fixture"):
            with self.subTest(kind=source.split(":")[0]):
                resource = cloudinary.CloudinaryResource(public_id=source)
                self.assertEqual(image_url(resource), PLACEHOLDER)


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


class ProductImageRenderingTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Image fixture", price="11.49", image=REFERENCE)

    def image(self, response):
        parser = Images()
        parser.feed(response.content.decode())
        return next(img for img in parser.images if img.get("alt") == self.product.name)

    def test_database_reference_renders_initial_cloudinary_src_and_browser_fallback(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Offline only")), patch("cloudinary.uploader.upload_resource") as upload:
            image = self.image(self.client.get(reverse("products:product_list")))
        self.assertEqual(image["src"], EXPECTED)
        self.assertIn(PLACEHOLDER, image["onerror"])
        self.assertIn("this.onerror=null", image["onerror"])
        upload.assert_not_called()
        self.product.refresh_from_db()
        self.assertEqual(self.product.image.get_prep_value(), REFERENCE)

    def test_missing_cloud_uses_placeholder_as_initial_src(self):
        with patch.object(cloudinary.config(), "cloud_name", None):
            image = self.image(self.client.get(reverse("products:product_list")))
        self.assertEqual(image["src"], PLACEHOLDER)
