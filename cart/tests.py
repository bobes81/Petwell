from django.test import Client, TestCase
from django.urls import reverse

from products.models import Product


class CartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Balm", price="7.25")
        self.add = reverse("cart:add_to_cart", args=[self.product.pk])
        self.remove = reverse("cart:remove_from_cart", args=[self.product.pk])

    def test_cart_mutations_require_post_and_csrf(self):
        for url in (self.add, self.remove):
            self.assertEqual(self.client.get(url).status_code, 405)
            self.assertEqual(
                Client(enforce_csrf_checks=True).post(url).status_code, 403
            )
        self.client.post(self.add)
        self.assertContains(self.client.get(reverse("cart:view_cart")), "7.25")
        self.client.post(self.remove)
        self.assertEqual(self.client.session["cart"], {})

    def test_missing_product_does_not_change_cart(self):
        self.assertEqual(
            self.client.post(
                reverse("cart:add_to_cart", args=[99999])
            ).status_code,
            404,
        )
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_stale_cart_can_be_displayed_and_removed(self):
        session = self.client.session
        session["cart"] = {"99999": 1}
        session.save()
        self.assertContains(
            self.client.get(reverse("cart:view_cart")), "Unavailable product"
        )
        self.client.post(reverse("cart:remove_from_cart", args=[99999]))
        self.assertEqual(self.client.session["cart"], {})
