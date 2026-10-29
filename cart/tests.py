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


class UnavailableCartTests(TestCase):
    def setUp(self):
        self.hidden = Product.objects.create(name="Withdrawn", price="4.99", is_available=False)

    def test_direct_add_rejected_and_cart_unchanged(self):
        response = self.client.post(reverse("cart:add_to_cart", args=[self.hidden.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_existing_unavailable_line_is_removable(self):
        session = self.client.session
        session["cart"] = {str(self.hidden.pk): 1}
        session.save()
        response = self.client.get(reverse("cart:view_cart"))
        self.assertContains(response, "Unavailable product")
        self.assertContains(response, "Remove unavailable items before checkout.")
        self.assertNotContains(response, "Proceed to Checkout")
        self.client.post(reverse("cart:remove_from_cart", args=[self.hidden.pk]))
        self.assertEqual(self.client.session["cart"], {})


class MixedAvailabilityCartTests(TestCase):
    def test_missing_line_blocks_mixed_cart_until_removed(self):
        active = Product.objects.create(name="Available fixture", price="7.25")
        missing_id = active.pk + 100000
        session = self.client.session
        session["cart"] = {str(active.pk): 2, str(missing_id): 1}
        session.save()
        response = self.client.get(reverse("cart:view_cart"))
        self.assertContains(response, "Unavailable product")
        self.assertContains(response, "14.50")
        self.assertNotContains(response, "Proceed to Checkout")
        self.client.post(reverse("cart:remove_from_cart", args=[missing_id]))
        self.assertEqual(self.client.session["cart"], {str(active.pk): 2})
        self.assertContains(self.client.get(reverse("cart:view_cart")), "Proceed to Checkout")

    def test_active_item_cannot_checkout_until_withdrawn_line_removed(self):
        active = Product.objects.create(name="Active", price="7.25")
        withdrawn = Product.objects.create(name="Withdrawn", price="4.99", is_available=False)
        session = self.client.session
        session["cart"] = {str(active.pk): 1, str(withdrawn.pk): 1}
        session.save()
        response = self.client.get(reverse("cart:view_cart"))
        self.assertContains(response, "Active")
        self.assertContains(response, "Remove unavailable items before checkout.")
        self.assertNotContains(response, "Proceed to Checkout")
        self.client.post(reverse("cart:remove_from_cart", args=[withdrawn.pk]))
        self.assertContains(self.client.get(reverse("cart:view_cart")), "Proceed to Checkout")

    def test_zero_price_line_is_not_counted_as_payable(self):
        invalid = Product.objects.create(name="No price", price="0.00")
        session = self.client.session
        session["cart"] = {str(invalid.pk): 1}
        session.save()
        response = self.client.get(reverse("cart:view_cart"))
        self.assertContains(response, "Unavailable product")
        self.assertNotContains(response, "Proceed to Checkout")

    def test_zero_price_cannot_be_added_directly(self):
        invalid = Product.objects.create(name="Not for sale", price="0.00")
        response = self.client.post(reverse("cart:add_to_cart", args=[invalid.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.session.get("cart", {}), {})
