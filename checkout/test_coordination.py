from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from types import SimpleNamespace
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.db import close_old_connections, connection
from django.test import RequestFactory, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from orders.models import CheckoutState, Order
from products.models import Product

from .coordination import CheckoutBusy, checkout_lease, session_digest
from .views import checkout


class CheckoutCoordinationTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Balm", price="7.25")
        self.store = SessionStore()
        self.store["cart"] = {str(self.product.pk): 1}
        self.store["cart_line_tokens"] = {str(self.product.pk): str(uuid4())}
        self.store.save()
        self.factory = RequestFactory()

    def request(self):
        request = self.factory.post(
            reverse("checkout:checkout"),
            {
                "name": "Buyer",
                "email": "buyer@example.test",
                "address": "Test",
            },
        )
        request.user = AnonymousUser()
        request.session = SessionStore(session_key=self.store.session_key)
        # Reproduce workers that have already loaded the same stale session.
        list(request.session.items())
        return request

    def test_preloaded_requests_share_active_order_before_middleware_save(
        self,
    ):
        first, second = self.request(), self.request()
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_one",
                status="open",
                url="https://checkout.stripe.com/one",
            ),
        ) as create:
            self.assertEqual(checkout(first).status_code, 302)
        with (
            patch(
                "checkout.views.stripe.checkout.Session.retrieve",
                return_value=SimpleNamespace(
                    id="cs_one",
                    status="open",
                    url="https://checkout.stripe.com/one",
                ),
            ) as retrieve,
            patch(
                "checkout.views.stripe.checkout.Session.create"
            ) as duplicate,
        ):
            self.assertEqual(checkout(second).status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        create.assert_called_once()
        retrieve.assert_called_once()
        duplicate.assert_not_called()

    def test_busy_lease_does_not_start_a_second_checkout(self):
        request = self.request()
        key = session_digest(request)
        token = uuid4()
        CheckoutState.objects.create(
            session_digest=key,
            processing_token=token,
            processing_until=timezone.now() + timedelta(seconds=60),
        )
        with patch("checkout.views.stripe.checkout.Session.create") as create:
            response = checkout(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"being processed", response.content)
        create.assert_not_called()
        self.assertFalse(Order.objects.exists())
        self.assertEqual(
            CheckoutState.objects.get(pk=key).processing_token, token
        )

    def test_expired_lease_can_be_recovered_and_is_released(self):
        request = self.request()
        key = session_digest(request)
        CheckoutState.objects.create(
            session_digest=key,
            processing_token=uuid4(),
            processing_until=timezone.now() - timedelta(seconds=1),
        )
        with checkout_lease(request) as lease:
            lease.assert_current()
        state = CheckoutState.objects.get(pk=key)
        self.assertIsNone(state.processing_token)
        self.assertIsNone(state.processing_until)

    def test_stale_holder_cannot_overwrite_or_release_new_holder(self):
        request = self.request()
        order = Order.objects.create(
            full_name="Buyer", email="buyer@example.test", address="Test"
        )
        with checkout_lease(request) as lease:
            replacement = uuid4()
            CheckoutState.objects.filter(pk=lease.key).update(
                processing_token=replacement
            )
            with self.assertRaises(CheckoutBusy):
                lease.set_order(order)
            with self.assertRaises(CheckoutBusy):
                lease.assert_current()
        state = CheckoutState.objects.get(pk=lease.key)
        self.assertEqual(state.processing_token, replacement)
        self.assertIsNone(state.active_order_id)

    def test_exception_releases_lease_and_keeps_durable_order_pointer(self):
        request = self.request()
        order = Order.objects.create(
            full_name="Buyer", email="buyer@example.test", address="Test"
        )
        with self.assertRaises(RuntimeError):
            with checkout_lease(request) as lease:
                lease.set_order(order)
                raise RuntimeError("interrupted")
        state = CheckoutState.objects.get(pk=session_digest(request))
        self.assertIsNone(state.processing_token)
        self.assertEqual(state.active_order_id, order.pk)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency check")
class CheckoutPostgresConcurrencyTests(TransactionTestCase):
    def test_overlapping_workers_cannot_create_two_payable_sessions(self):
        product = Product.objects.create(
            name="Concurrency fixture", price="7.25"
        )
        store = SessionStore()
        store["cart"] = {str(product.pk): 1}
        store["cart_line_tokens"] = {str(product.pk): str(uuid4())}
        store.save()
        session_key = store.session_key
        entered, release = Event(), Event()

        def create_session(**kwargs):
            entered.set()
            if not release.wait(5):
                raise AssertionError("Checkout worker was not released")
            return SimpleNamespace(
                id="cs_parallel",
                status="open",
                url="https://checkout.stripe.com/parallel",
            )

        def post_checkout():
            close_old_connections()
            try:
                request = RequestFactory().post(
                    reverse("checkout:checkout"),
                    {
                        "name": "Buyer",
                        "email": "buyer@example.test",
                        "address": "Local fixture",
                    },
                )
                request.user = AnonymousUser()
                request.session = SessionStore(session_key=session_key)
                return checkout(request)
            finally:
                close_old_connections()

        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=create_session,
        ) as create:
            with ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(post_checkout)
                try:
                    self.assertTrue(entered.wait(5))
                    second = pool.submit(post_checkout).result(timeout=5)
                    self.assertEqual(second.status_code, 200)
                    self.assertIn(b"already being processed", second.content)
                finally:
                    release.set()
                self.assertEqual(first.result(timeout=5).status_code, 302)
        create.assert_called_once()
        self.assertEqual(Order.objects.count(), 1)
