from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
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

    def test_staff_shop_account_cannot_browse_or_reorder_another_users_order(self):
        self.other.is_staff = True
        self.other.save(update_fields=["is_staff"])
        self.client.force_login(self.other)
        self.assertContains(self.client.get(self.url), "You have no orders yet")
        self.assertNotContains(
            self.client.get(self.url), str(self.order.public_id)
        )
        self.assertEqual(self.client.post(self.reorder).status_code, 404)
        self.assertEqual(
            self.client.get(
                reverse("checkout:success", args=[self.order.public_id])
            ).status_code,
            404,
        )
        self.assertNotIn("cart", self.client.session)
        self.order.refresh_from_db()
        self.assertEqual(self.order.user_id, self.user.pk)
        self.assertEqual(self.order.status, "paid")

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
    def test_confirmed_commerce_and_blog_history_upgrades_without_data_loss(self):
        # Reconstruct only the reported history plus its required dependencies
        # inside Django's isolated test database. Never downgrade production.
        before = [
            ("orders", "0001_initial"),
            ("products", "0001_initial"),
            ("blog", "0004_merge_20260213_0814"),
        ]
        executor = MigrationExecutor(connection)
        after = executor.loader.graph.leaf_nodes()
        try:
            executor.migrate([
                (app, None) for app in sorted({app for app, _ in after})
            ])
            executor = MigrationExecutor(connection)
            executor.migrate(before)
            expected_history = {
                node
                for target in before
                for node in executor.loader.graph.forwards_plan(target)
            }
            self.assertEqual(
                set(MigrationRecorder(connection).applied_migrations()),
                expected_history,
            )
            # Both historical blog branches are already applied. Only the
            # pending project migrations may run during this forward upgrade.
            plan = MigrationExecutor(connection).migration_plan(after)
            self.assertTrue(all(not backwards for _, backwards in plan))
            self.assertEqual(
                {
                    (migration.app_label, migration.name)
                    for migration, _ in plan
                    if migration.app_label in {
                        "orders", "products", "blog", "accounts"
                    }
                },
                {
                    ("accounts", "0001_initial"),
                    (
                        "orders",
                        "0002_order_paid_at_order_public_id_order_status_and_more",
                    ),
                    ("orders", "0003_alter_orderitem_product"),
                    (
                        "orders",
                        "0004_order_cart_line_tokens_order_stripe_checkout_payload",
                    ),
                    ("orders", "0005_checkoutstate"),
                },
            )
            old_apps = executor.loader.project_state(before).apps
            LegacyUser = old_apps.get_model("auth", "User")
            LegacyProduct = old_apps.get_model("products", "Product")
            LegacyOrder = old_apps.get_model("orders", "Order")
            LegacyItem = old_apps.get_model("orders", "OrderItem")
            user = LegacyUser.objects.create(
                username="migration-member", email="member@example.test"
            )
            product = LegacyProduct.objects.create(
                name="Legacy balm", description="Synthetic migration fixture",
                price="8.50", image="legacy-image",
            )
            legacy_post = old_apps.get_model("blog", "BlogPost").objects.create(
                author_id=user.pk,
                title="Existing blog fixture",
                content="Preserve this synthetic story during the upgrade.",
                image="legacy-blog-image",
            )
            legacy_subscriber = old_apps.get_model(
                "blog", "Subscriber"
            ).objects.create(email="existing-subscriber@example.test")
            snapshots = {}
            for name, owner in (("First customer", user), ("Second customer", None)):
                order = LegacyOrder.objects.create(
                    user=owner,
                    full_name=name,
                    email="legacy@example.test",
                    address="Legacy",
                    total_price="14.50",
                )
                item = LegacyItem.objects.create(
                    order=order, product=product, quantity=2, price="7.25"
                )
                snapshots[order.pk] = {
                    "full_name": name, "user_id": getattr(owner, "pk", None),
                    "email": order.email, "address": order.address,
                    "total_price": order.total_price,
                    "created_at": order.created_at, "item_pk": item.pk,
                }
            executor = MigrationExecutor(connection)
            executor.migrate(after)
            # Old workers do not supply the new required application-default
            # fields. A release must stop those writes before schema cutover.
            with self.assertRaises(IntegrityError):
                with transaction.atomic():
                    LegacyOrder.objects.create(
                        full_name="Old worker fixture",
                        email="old-worker@example.test",
                        address="Local only",
                        total_price="1.00",
                    )
            apps = executor.loader.project_state(after).apps
            MigratedOrder = apps.get_model("orders", "Order")
            MigratedItem = apps.get_model("orders", "OrderItem")
            MigratedProduct = apps.get_model("products", "Product")
            orders = list(MigratedOrder.objects.all())
            self.assertEqual(len(orders), 2)
            self.assertEqual(len({order.public_id for order in orders}), 2)
            self.assertTrue(
                all(
                    order.status == "pending" and order.paid_at is None
                    for order in orders
                )
            )
            for order in orders:
                snapshot = snapshots[order.pk]
                for field in (
                    "full_name", "user_id", "email", "address", "created_at"
                ):
                    self.assertEqual(getattr(order, field), snapshot[field])
                self.assertEqual(order.total_price, Decimal(snapshot["total_price"]))
                self.assertIsNone(order.stripe_session_id)
                self.assertEqual(order.cart_line_tokens, {})
                self.assertEqual(order.stripe_checkout_payload, {})
                item = MigratedItem.objects.get(pk=snapshot["item_pk"])
                self.assertEqual(item.order_id, order.pk)
                self.assertEqual(item.product_id, product.pk)
                self.assertEqual(item.quantity, 2)
                self.assertEqual(item.price, Decimal("7.25"))
            migrated_product = MigratedProduct.objects.get(pk=product.pk)
            self.assertEqual(migrated_product.name, product.name)
            self.assertEqual(migrated_product.description, product.description)
            self.assertEqual(migrated_product.price, Decimal("8.50"))
            self.assertEqual(str(migrated_product.image), "legacy-image")
            with self.assertRaises(ProtectedError):
                migrated_product.delete()

            migrated_post = apps.get_model("blog", "BlogPost").objects.get(
                pk=legacy_post.pk
            )
            for field in ("author_id", "title", "content", "created_at"):
                self.assertEqual(
                    getattr(migrated_post, field), getattr(legacy_post, field)
                )
            self.assertEqual(str(migrated_post.image), "legacy-blog-image")
            migrated_subscriber = apps.get_model(
                "blog", "Subscriber"
            ).objects.get(pk=legacy_subscriber.pk)
            self.assertEqual(migrated_subscriber.email, legacy_subscriber.email)
            self.assertEqual(
                migrated_subscriber.subscribed_at, legacy_subscriber.subscribed_at
            )

            # Exercise new tables and writes to the existing blog tables,
            # instead of checking only that migration names were recorded.
            profile = apps.get_model("accounts", "PetProfile").objects.create(
                owner_id=user.pk, name="Fixture pet", species="dog",
                care_focus="general",
            )
            self.assertEqual(profile.owner_id, user.pk)
            state = apps.get_model("orders", "CheckoutState").objects.create(
                session_digest="f" * 64, active_order_id=orders[0].pk
            )
            self.assertIsNone(state.processing_token)
            self.assertIsNone(state.processing_until)
            with self.assertRaises(ProtectedError):
                orders[0].delete()
            apps.get_model("blog", "BlogPost").objects.create(
                author_id=user.pk, title="Migration fixture", content="Local only"
            )
            apps.get_model("blog", "Subscriber").objects.create(
                email="subscriber@example.test"
            )
            final_executor = MigrationExecutor(connection)
            final_executor.loader.check_consistent_history(connection)
            self.assertEqual(final_executor.migration_plan(after), [])
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
