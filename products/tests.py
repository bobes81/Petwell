from contextlib import redirect_stdout
from decimal import Decimal
from io import StringIO

from django.test import TestCase

from .models import Product
from .seed import run


class SampleCatalogueTests(TestCase):
    def seed(self):
        with redirect_stdout(StringIO()):
            run()

    def test_fresh_seed_does_not_offer_unimplemented_download_fulfilment(self):
        self.seed()
        self.assertEqual(Product.objects.count(), 9)
        self.assertFalse(Product.objects.filter(name__icontains="PDF").exists())
        self.assertFalse(
            Product.objects.filter(description__icontains="download").exists()
        )
        self.assertFalse(Product.objects.filter(price__lte=0).exists())

    def test_reseeding_preserves_existing_catalogue_and_legacy_pdf(self):
        product = Product.objects.create(
            name="Calming Lavender Spray",
            description="Owner-reviewed description, not a sample overwrite.",
            price=Decimal("17.25"),
            image="catalogue/owner-image",
        )
        legacy_pdf = Product.objects.create(
            name="Mindful Pet Journal (PDF)",
            description="Legacy offer requiring owner fulfilment review.",
            price=Decimal("4.99"),
        )
        self.seed()
        original_rows = list(
            Product.objects.order_by("pk").values(
                "pk", "name", "description", "price"
            )
        )
        self.seed()
        self.assertEqual(
            list(
                Product.objects.order_by("pk").values(
                    "pk", "name", "description", "price"
                )
            ),
            original_rows,
        )
        self.assertEqual(Product.objects.count(), 10)
        product.refresh_from_db()
        self.assertEqual(product.price, Decimal("17.25"))
        self.assertEqual(
            product.description,
            "Owner-reviewed description, not a sample overwrite.",
        )
        self.assertEqual(str(product.image), "catalogue/owner-image")
        self.assertTrue(Product.objects.filter(pk=legacy_pdf.pk).exists())


class ProductAvailabilityTests(TestCase):
    def test_negative_price_is_hidden_and_cannot_be_added_directly(self):
        from django.urls import reverse

        product = Product.objects.create(name="Invalid price fixture", price="-1.00")
        self.assertNotContains(self.client.get(reverse("products:product_list")), product.name)
        self.assertEqual(
            self.client.post(reverse("cart:add_to_cart", args=[product.pk])).status_code,
            404,
        )
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_reseeding_does_not_reactivate_withdrawn_rows(self):
        products = [
            Product.objects.create(name=name, price="4.99", is_available=False)
            for name in ("Calming Lavender Spray", "Mindful Pet Journal (PDF)")
        ]
        with redirect_stdout(StringIO()):
            run()
        for product in products:
            product.refresh_from_db()
            self.assertFalse(product.is_available)
            self.assertEqual(product.price, Decimal("4.99"))

    def test_unavailable_product_is_not_listed_but_preserved(self):
        hidden = Product.objects.create(name="Mindful Pet Journal (PDF)", price="4.99", is_available=False)
        visible = Product.objects.create(name="Physical balm", price="7.25")
        from django.urls import reverse
        response = self.client.get(reverse("products:product_list"))
        self.assertContains(response, visible.name)
        self.assertNotContains(response, hidden.name)
        self.assertTrue(Product.objects.filter(pk=hidden.pk).exists())

    def test_zero_price_product_is_not_listed(self):
        hidden = Product.objects.create(name="Unpriced sample", price="0.00")
        visible = Product.objects.create(name="Priced product", price="7.25")
        from django.urls import reverse
        response = self.client.get(reverse("products:product_list"))
        self.assertContains(response, visible.name)
        self.assertNotContains(response, hidden.name)
