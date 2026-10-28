from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from products.models import Product

from .models import Order, OrderItem


class OrderHistoryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("buyer")
        self.other = get_user_model().objects.create_user("other")
        self.product = Product.objects.create(name="Balm", price="8.50")
        self.order = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.test",
            address="Test",
            status="paid",
            total_price="14.50",
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price="7.25"
        )
        self.url = reverse("orders:history")
        self.reorder = reverse("orders:reorder", args=[self.order.public_id])

    def test_login_required(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)
        self.assertEqual(self.client.post(self.reorder).status_code, 302)

    def test_only_own_orders_displayed(self):
        self.client.force_login(self.other)
        self.assertNotContains(
            self.client.get(self.url), str(self.order.public_id)
        )
        self.assertEqual(self.client.post(self.reorder).status_code, 404)
        self.client.force_login(self.user)
        self.assertContains(
            self.client.get(self.url), str(self.order.public_id)
        )

    def test_reorder_post_adds_items_using_current_product_price(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.reorder).status_code, 405)
        self.assertRedirects(
            self.client.post(self.reorder), reverse("cart:view_cart")
        )
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 2)
        self.assertContains(
            self.client.get(reverse("cart:view_cart")), "17.00"
        )
        self.order.refresh_from_db()
        self.assertEqual(str(self.order.total_price), "14.50")

    def test_pending_order_cannot_be_reordered(self):
        self.order.status = "pending"
        self.order.save()
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(self.reorder).status_code, 404)

    def test_order_items_prevent_destructive_product_deletion(self):
        with self.assertRaises(ProtectedError):
            self.product.delete()


class ExistingOrdersMigrationTests(TransactionTestCase):
    def test_multiple_legacy_orders_get_distinct_ids_and_remain_unpaid(self):
        before = [("orders", "0001_initial")]
        after = [
            (
                "orders",
                "0005_checkoutstate",
            )
        ]
        executor = MigrationExecutor(connection)
        executor.migrate(before)
        try:
            old_apps = executor.loader.project_state(before).apps
            LegacyOrder = old_apps.get_model("orders", "Order")
            for name in ("First customer", "Second customer"):
                LegacyOrder.objects.create(
                    full_name=name,
                    email="legacy@example.test",
                    address="Legacy",
                    total_price="10.00",
                )
            executor = MigrationExecutor(connection)
            executor.migrate(after)
            apps = executor.loader.project_state(after).apps
            MigratedOrder = apps.get_model("orders", "Order")
            orders = list(MigratedOrder.objects.all())
            self.assertEqual(len(orders), 2)
            self.assertEqual(len({order.public_id for order in orders}), 2)
            self.assertTrue(
                all(
                    order.status == "pending" and order.paid_at is None
                    for order in orders
                )
            )
        finally:
            MigrationExecutor(connection).migrate(after)


class OrderAdminProtectionTests(TestCase):
    def test_payment_order_cannot_be_deleted_even_by_superuser(self):
        user = get_user_model().objects.create_superuser(
            "admin",
            email="admin@example.test",
            password="LocalAdminPass492!",
        )
        order = Order.objects.create(
            full_name="Buyer",
            email="buyer@example.test",
            address="Test",
            stripe_session_id="cs_payable",
            total_price="14.50",
        )
        self.client.force_login(user)
        url = reverse("admin:orders_order_delete", args=[order.pk])
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(
            self.client.post(url, {"post": "yes"}).status_code, 403
        )
        self.assertTrue(Order.objects.filter(pk=order.pk).exists())
