import hashlib
import hmac
import json
import time
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import stripe
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from orders.models import Order
from products.models import Product


class CheckoutTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Paw balm", description="Care", price="7.25"
        )
        session = self.client.session
        session["cart"] = {str(self.product.pk): 2}
        session.save()
        self.data = {
            "name": "Test Customer",
            "email": "customer@example.test",
            "address": "1 Test Road",
        }
        self.url = reverse("checkout:checkout")

    def create_order(self):
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_test_123", url="https://checkout.stripe.com/test"
            ),
        ) as create:
            response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        return Order.objects.get(), create

    def event(self, order, **changes):
        obj = {
            "id": order.stripe_session_id,
            "mode": "payment",
            "payment_status": "paid",
            "currency": "gbp",
            "amount_total": 1450,
            "metadata": {"order_id": str(order.public_id)},
            "client_reference_id": str(order.public_id),
            "livemode": False,
        }
        obj.update(changes)
        return {
            "id": "evt_test",
            "type": "checkout.session.completed",
            "data": {"object": obj},
        }

    def webhook(self, event, secret="whsec_offline"):
        payload = json.dumps(event).encode()
        timestamp = str(int(time.time()))
        signature = hmac.new(
            secret.encode(),
            timestamp.encode() + b"." + payload,
            hashlib.sha256,
        ).hexdigest()
        return self.client.post(
            reverse("checkout:webhook"),
            payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=f"t={timestamp},v1={signature}",
        )

    def test_checkout_uses_server_prices_and_leaves_order_unpaid(self):
        self.data["total"] = "0.01"
        order, create = self.create_order()
        self.assertEqual(order.status, "pending")
        self.assertIsNone(order.paid_at)
        self.assertEqual(order.total_price, Decimal("14.50"))
        self.assertEqual(order.items.get().quantity, 2)
        self.assertEqual(
            create.call_args.kwargs["line_items"][0]["price_data"][
                "unit_amount"
            ],
            725,
        )
        self.assertIn("idempotency_key", create.call_args.kwargs)
        self.assertEqual(
            self.client.session["cart"], {str(self.product.pk): 2}
        )

    def test_repeat_submission_reuses_order_and_idempotency_key(self):
        order, first = self.create_order()
        again, second = self.create_order()
        self.assertEqual(order.pk, again.pk)
        self.assertEqual(first.call_args.kwargs, second.call_args.kwargs)

    def test_invalid_form_does_not_create_order(self):
        self.data["email"] = "invalid"
        self.assertContains(
            self.client.post(self.url, self.data),
            "Enter a valid email address",
        )
        self.assertFalse(Order.objects.exists())

    def test_empty_stale_negative_and_noninteger_cart_rejected(self):
        for cart in (
            {},
            {"99999": 1},
            {str(self.product.pk): -1},
            {str(self.product.pk): True},
            {str(self.product.pk): 100},
            {str(self.product.pk): "2"},
        ):
            with self.subTest(cart=cart):
                session = self.client.session
                session["cart"] = cart
                session.save()
                self.assertEqual(
                    self.client.post(self.url, self.data).status_code, 400
                )
        self.assertFalse(Order.objects.exists())

    @override_settings(STRIPE_SECRET_KEY="")
    def test_missing_key_keeps_cart_and_shows_error(self):
        self.assertContains(
            self.client.post(self.url, self.data), "temporarily unavailable"
        )
        self.assertFalse(Order.objects.exists())
        self.assertTrue(self.client.session["cart"])

    @override_settings(
        STRIPE_SECRET_KEY="sk_live_not_allowed", STRIPE_LIVE_MODE=False
    )
    def test_live_key_is_blocked_when_test_mode_configured(self):
        with patch("checkout.views.stripe.checkout.Session.create") as create:
            self.assertContains(
                self.client.post(self.url, self.data),
                "temporarily unavailable",
            )
            create.assert_not_called()

    def test_stripe_error_is_recoverable(self):
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=stripe.APIConnectionError("offline"),
        ):
            self.assertContains(
                self.client.post(self.url, self.data),
                "could not start payment",
            )
        self.assertEqual(Order.objects.get().status, "pending")
        self.assertTrue(self.client.session["cart"])

    def test_return_url_does_not_confirm_payment_or_clear_cart(self):
        order, _ = self.create_order()
        self.assertContains(
            self.client.get(
                reverse("checkout:success", args=[order.public_id])
            ),
            "Awaiting payment confirmation",
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")
        self.assertTrue(self.client.session["cart"])

    def test_valid_signed_webhook_confirms_once_and_return_clears_once(self):
        order, _ = self.create_order()
        event = self.event(order)
        self.assertEqual(self.webhook(event).status_code, 200)
        order.refresh_from_db()
        paid_at = order.paid_at
        self.assertEqual(order.status, "paid")
        self.assertIsNotNone(paid_at)
        self.assertEqual(self.webhook(event).status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.paid_at, paid_at)
        url = reverse("checkout:success", args=[order.public_id])
        self.assertContains(self.client.get(url), "Payment confirmed")
        self.assertEqual(self.client.session["cart"], {})
        session = self.client.session
        session["cart"] = {str(self.product.pk): 1}
        session.save()
        self.client.get(url)
        self.assertEqual(
            self.client.session["cart"], {str(self.product.pk): 1}
        )

    def test_paid_return_preserves_additional_cart_items(self):
        order, _ = self.create_order()
        self.webhook(self.event(order))
        session = self.client.session
        session["cart"] = {str(self.product.pk): 3}
        session.save()
        self.client.get(reverse("checkout:success", args=[order.public_id]))
        self.assertEqual(
            self.client.session["cart"], {str(self.product.pk): 1}
        )

    def test_bad_signature_and_malformed_payload_rejected(self):
        order, _ = self.create_order()
        self.assertEqual(
            self.webhook(self.event(order), secret="wrong").status_code, 400
        )
        self.assertEqual(
            self.client.post(
                reverse("checkout:webhook"),
                "not json",
                content_type="application/json",
            ).status_code,
            400,
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")

    def test_wrong_amount_currency_order_reference_and_mode_rejected(self):
        order, _ = self.create_order()
        for change in (
            {"amount_total": 1},
            {"currency": "usd"},
            {"metadata": {"order_id": "other"}},
            {"client_reference_id": "other"},
            {"mode": "subscription"},
            {"livemode": True},
        ):
            with self.subTest(change=change):
                self.assertEqual(
                    self.webhook(self.event(order, **change)).status_code, 400
                )
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")

    def test_unpaid_event_never_marks_paid(self):
        order, _ = self.create_order()
        self.assertEqual(
            self.webhook(
                self.event(order, payment_status="unpaid")
            ).status_code,
            200,
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")

    def test_unknown_session_requests_retry(self):
        order, _ = self.create_order()
        self.assertEqual(
            self.webhook(self.event(order, id="cs_not_saved_yet")).status_code,
            503,
        )

    def test_other_browser_cannot_read_guest_order(self):
        order, _ = self.create_order()
        self.assertEqual(
            Client()
            .get(reverse("checkout:success", args=[order.public_id]))
            .status_code,
            404,
        )

    def test_checkout_requires_csrf_but_signed_webhook_does_not(self):
        c = Client(enforce_csrf_checks=True)
        self.assertEqual(c.post(self.url, self.data).status_code, 403)
        self.assertEqual(
            c.post(
                reverse("checkout:webhook"),
                b"{}",
                content_type="application/json",
            ).status_code,
            400,
        )

    def test_paid_cart_clears_on_cart_visit_without_return_url(self):
        order, _ = self.create_order()
        self.webhook(self.event(order))
        self.assertContains(
            self.client.get(reverse("cart:view_cart")), "Your cart is empty"
        )
        self.assertEqual(self.client.session["cart"], {})

    def test_async_success_confirms_but_unrelated_event_is_ignored(self):
        order, _ = self.create_order()
        event = self.event(order)
        event["type"] = "payment_intent.created"
        self.assertEqual(self.webhook(event).status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")
        event["type"] = "checkout.session.async_payment_succeeded"
        self.assertEqual(self.webhook(event).status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, "paid")
