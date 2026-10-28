import hashlib
import hmac
import json
import time
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import stripe
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from orders.models import CheckoutState, Order
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
        retrieve = patch(
            "checkout.views.stripe.checkout.Session.retrieve",
            return_value=SimpleNamespace(
                id="cs_test_123",
                status="open",
                url="https://checkout.stripe.com/test",
            ),
        )
        self.retrieve = retrieve.start()
        self.addCleanup(retrieve.stop)

    def create_order(self):
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_test_123",
                status="open",
                url="https://checkout.stripe.com/test",
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

    def webhook(self, event, secret="whsec_offline", timestamp=None, client=None):
        payload = json.dumps(event).encode()
        timestamp = str(int(time.time()) if timestamp is None else timestamp)
        signature = hmac.new(
            secret.encode(),
            timestamp.encode() + b"." + payload,
            hashlib.sha256,
        ).hexdigest()
        return (client or self.client).post(
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
        self.assertTrue(first.called)
        second.assert_not_called()
        self.retrieve.assert_called_once_with(
            order.stripe_session_id,
            api_key="sk_test_offline",
        )

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

    def test_cookieless_webhook_with_csrf_checks_requires_valid_signature(self):
        order, _ = self.create_order()
        sender = Client(enforce_csrf_checks=True)
        event = self.event(order)
        self.assertEqual(
            self.webhook(event, secret="wrong", client=sender).status_code,
            400,
        )
        self.assertFalse(sender.cookies)
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")
        self.assertIsNone(order.paid_at)

        self.assertEqual(self.webhook(event, client=sender).status_code, 200)
        self.assertFalse(sender.cookies)
        order.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertIsNotNone(order.paid_at)
        self.assertEqual(Order.objects.count(), 1)
        # Stripe's separate HTTP request cannot modify a customer's session.
        self.assertEqual(
            self.client.session["cart"], {str(self.product.pk): 2}
        )
        self.assertContains(
            self.client.get(reverse("cart:view_cart")), "Your cart is empty"
        )
        self.assertEqual(self.client.session["cart"], {})

    def test_delayed_failure_and_distinct_success_events_preserve_paid_order(self):
        order, _ = self.create_order()
        for event_type in (
            "checkout.session.completed",
            "checkout.session.async_payment_failed",
        ):
            event = self.event(order, payment_status="unpaid")
            event["type"] = event_type
            self.assertEqual(self.webhook(event).status_code, 200)
            order.refresh_from_db()
            self.assertEqual(order.status, "pending")
            self.assertIsNone(order.paid_at)
            self.assertEqual(
                self.client.session["cart"], {str(self.product.pk): 2}
            )

        success = self.event(order)
        success["id"] = "evt_async_success_fixture"
        success["type"] = "checkout.session.async_payment_succeeded"
        self.assertEqual(self.webhook(success).status_code, 200)
        order.refresh_from_db()
        paid_at = order.paid_at
        self.assertEqual(order.status, "paid")
        self.assertIsNotNone(paid_at)
        self.client.get(reverse("cart:view_cart"))
        self.assertEqual(self.client.session["cart"], {})
        self.client.post(reverse("cart:add_to_cart", args=[self.product.pk]))

        for number, (event_type, payment_status) in enumerate((
            ("checkout.session.completed", "paid"),
            ("checkout.session.async_payment_succeeded", "paid"),
            ("checkout.session.async_payment_failed", "unpaid"),
            ("checkout.session.expired", "unpaid"),
            ("checkout.session.completed", "unpaid"),
        )):
            with self.subTest(event_type=event_type, status=payment_status):
                delayed = self.event(order, payment_status=payment_status)
                delayed["id"] = f"evt_delayed_fixture_{number}"
                delayed["type"] = event_type
                self.assertEqual(self.webhook(delayed).status_code, 200)
                order.refresh_from_db()
                self.assertEqual(order.status, "paid")
                self.assertEqual(order.paid_at, paid_at)
                self.assertEqual(Order.objects.count(), 1)
                self.client.get(reverse("cart:view_cart"))
                self.assertEqual(
                    self.client.session["cart"], {str(self.product.pk): 1}
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

    def test_lost_session_response_retry_uses_frozen_product_name(self):
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=stripe.APIConnectionError("lost response"),
        ) as first:
            self.client.post(self.url, self.data)
        order = Order.objects.get()
        self.product.name = "Renamed balm"
        self.product.save()
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_recovered",
                status="open",
                url="https://checkout.stripe.com/recovered",
            ),
        ) as retry:
            self.assertEqual(
                self.client.post(self.url, self.data).status_code, 302
            )
        self.assertEqual(Order.objects.get().pk, order.pk)
        self.assertEqual(first.call_args.kwargs, retry.call_args.kwargs)

    def test_delayed_payment_does_not_remove_newly_readded_product(self):
        order, _ = self.create_order()
        self.client.post(
            reverse("cart:remove_from_cart", args=[self.product.pk])
        )
        self.client.post(reverse("cart:add_to_cart", args=[self.product.pk]))
        self.webhook(self.event(order))
        self.client.get(reverse("cart:view_cart"))
        self.assertEqual(
            self.client.session["cart"], {str(self.product.pk): 1}
        )

    @override_settings(STRIPE_WEBHOOK_SECRET="")
    def test_missing_webhook_configuration_blocks_checkout(self):
        with patch("checkout.views.stripe.checkout.Session.create") as create:
            self.assertContains(
                self.client.post(self.url, self.data),
                "temporarily unavailable",
            )
            create.assert_not_called()
        self.assertFalse(Order.objects.exists())

    def test_expired_session_renews_order_without_overwriting_old_mapping(
        self,
    ):
        old, _ = self.create_order()
        self.retrieve.return_value = SimpleNamespace(
            id=old.stripe_session_id,
            status="expired",
            url=None,
        )
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_new",
                status="open",
                url="https://checkout.stripe.com/new",
            ),
        ) as create:
            response = self.client.post(self.url, self.data)
        self.assertEqual(response.url, "https://checkout.stripe.com/new")
        self.assertEqual(Order.objects.count(), 2)
        new = Order.objects.exclude(pk=old.pk).get()
        self.assertEqual(
            create.call_args.kwargs["idempotency_key"],
            f"order-{new.public_id}",
        )
        self.assertNotEqual(old.public_id, new.public_id)
        old.refresh_from_db()
        self.assertEqual(old.stripe_session_id, "cs_test_123")
        self.assertEqual(old.status, "pending")

    def test_cached_expired_create_response_is_renewed_after_lost_response(
        self,
    ):
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=stripe.APIConnectionError("lost"),
        ):
            self.client.post(self.url, self.data)
        old = Order.objects.get()
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=[
                SimpleNamespace(id="cs_expired", status="expired", url=None),
                SimpleNamespace(
                    id="cs_new",
                    status="open",
                    url="https://checkout.stripe.com/new",
                ),
            ],
        ) as create:
            response = self.client.post(self.url, self.data)
        self.assertEqual(response.url, "https://checkout.stripe.com/new")
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(
            create.call_args_list[0].kwargs["idempotency_key"],
            f"order-{old.public_id}",
        )
        self.assertNotEqual(
            create.call_args_list[0].kwargs["idempotency_key"],
            create.call_args_list[1].kwargs["idempotency_key"],
        )
        old.refresh_from_db()
        self.assertEqual(old.stripe_session_id, "cs_expired")

    def test_completed_session_waits_for_webhook_without_new_payment(self):
        order, _ = self.create_order()
        self.retrieve.return_value = SimpleNamespace(
            id=order.stripe_session_id,
            status="complete",
            payment_status="paid",
            url=None,
        )
        with patch("checkout.views.stripe.checkout.Session.create") as create:
            response = self.client.post(self.url, self.data)
        self.assertEqual(
            response.url, reverse("checkout:success", args=[order.public_id])
        )
        create.assert_not_called()
        self.assertEqual(Order.objects.count(), 1)
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")
        self.assertTrue(self.client.session["cart"])

    def test_session_retrieval_error_preserves_existing_attempt(self):
        order, _ = self.create_order()
        self.retrieve.side_effect = stripe.APIConnectionError("offline")
        with patch("checkout.views.stripe.checkout.Session.create") as create:
            self.assertContains(
                self.client.post(self.url, self.data),
                "could not start payment",
            )
        create.assert_not_called()
        order.refresh_from_db()
        self.assertEqual(order.stripe_session_id, "cs_test_123")
        self.assertEqual(order.status, "pending")
        self.assertEqual(Order.objects.count(), 1)
        self.assertTrue(self.client.session["cart"])

    def test_retry_after_cart_key_reordering_uses_original_payload(self):
        other = Product.objects.create(name="Chew", price="3.00")
        session = self.client.session
        session["cart"][str(other.pk)] = 1
        session.save()
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=stripe.APIConnectionError("lost"),
        ) as first:
            self.client.post(self.url, self.data)
        session = self.client.session
        session["cart"] = dict(reversed(list(session["cart"].items())))
        session.save()
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_recovered",
                status="open",
                url="https://checkout.stripe.com/recovered",
            ),
        ) as retry:
            self.assertEqual(
                self.client.post(self.url, self.data).status_code, 302
            )
        self.assertEqual(first.call_args.kwargs, retry.call_args.kwargs)
        self.assertEqual(Order.objects.count(), 1)

    def test_legacy_attempt_without_payload_gets_fresh_order_and_key(self):
        from orders.models import OrderItem

        legacy = Order.objects.create(
            full_name=self.data["name"],
            email=self.data["email"],
            address=self.data["address"],
            total_price="14.50",
        )
        OrderItem.objects.create(
            order=legacy,
            product=self.product,
            quantity=2,
            price=self.product.price,
        )
        session = self.client.session
        session["pending_order"] = str(legacy.public_id)
        session.save()
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_fresh",
                status="open",
                url="https://checkout.stripe.com/new",
            ),
        ) as create:
            self.assertEqual(
                self.client.post(self.url, self.data).status_code, 302
            )
        self.assertEqual(Order.objects.count(), 2)
        self.assertNotEqual(
            create.call_args.kwargs["idempotency_key"],
            f"order-{legacy.public_id}",
        )
        legacy.refresh_from_db()
        self.assertIsNone(legacy.stripe_session_id)

    def test_expired_signature_is_rejected(self):
        order, _ = self.create_order()
        response = self.webhook(
            self.event(order), timestamp=int(time.time()) - 1000
        )
        self.assertEqual(response.status_code, 400)
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")

    def test_signed_malformed_event_is_rejected_without_server_error(self):
        for event in (
            [],
            None,
            {},
            {"type": None},
            {"type": "checkout.session.completed"},
            {
                "type": "checkout.session.completed",
                "data": {"object": "not-a-session"},
            },
        ):
            with self.subTest(event=event):
                self.assertEqual(self.webhook(event).status_code, 400)

    def test_missing_live_mode_or_order_metadata_cannot_confirm_payment(self):
        order, _ = self.create_order()
        for change in (
            {"livemode": None},
            {"metadata": None},
            {"metadata": []},
        ):
            with self.subTest(change=change):
                self.assertEqual(
                    self.webhook(self.event(order, **change)).status_code, 400
                )
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")

    def test_completed_session_with_changed_contact_cannot_start_new_payment(
        self,
    ):
        order, _ = self.create_order()
        self.retrieve.return_value = SimpleNamespace(
            id=order.stripe_session_id, status="complete", url=None
        )
        changed = {**self.data, "address": "A corrected delivery address"}
        with (
            patch("checkout.views.stripe.checkout.Session.create") as create,
            patch("checkout.views.stripe.checkout.Session.expire") as expire,
        ):
            response = self.client.post(self.url, changed)
        self.assertEqual(
            response.url, reverse("checkout:success", args=[order.public_id])
        )
        create.assert_not_called()
        expire.assert_not_called()
        self.assertEqual(Order.objects.count(), 1)
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.address, self.data["address"])

    def test_completed_session_with_changed_cart_cannot_start_new_payment(
        self,
    ):
        order, _ = self.create_order()
        self.retrieve.return_value = SimpleNamespace(
            id=order.stripe_session_id, status="complete", url=None
        )
        session = self.client.session
        session["cart"][str(self.product.pk)] = 3
        session.save()
        with patch("checkout.views.stripe.checkout.Session.create") as create:
            response = self.client.post(self.url, self.data)
        self.assertEqual(
            response.url, reverse("checkout:success", args=[order.public_id])
        )
        create.assert_not_called()
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(
            self.client.session["cart"], {str(self.product.pk): 3}
        )

    def test_changed_cart_expires_existing_session_before_creating_replacement(
        self,
    ):
        old, _ = self.create_order()
        session = self.client.session
        session["cart"][str(self.product.pk)] = 3
        session.save()
        calls = []

        def retrieve(*args, **kwargs):
            calls.append("retrieve")
            return SimpleNamespace(
                id=old.stripe_session_id,
                status="open",
                url="https://checkout.stripe.com/old",
            )

        def expire(*args, **kwargs):
            calls.append("expire")
            return SimpleNamespace(
                id=old.stripe_session_id, status="expired", url=None
            )

        def create(*args, **kwargs):
            calls.append("create")
            return SimpleNamespace(
                id="cs_replacement",
                status="open",
                url="https://checkout.stripe.com/replacement",
            )

        self.retrieve.side_effect = retrieve
        with (
            patch(
                "checkout.views.stripe.checkout.Session.expire",
                side_effect=expire,
            ) as expiration,
            patch(
                "checkout.views.stripe.checkout.Session.create",
                side_effect=create,
            ),
        ):
            response = self.client.post(self.url, self.data)
        self.assertEqual(calls, ["retrieve", "expire", "create"])
        expiration.assert_called_once_with(
            old.stripe_session_id, api_key="sk_test_offline"
        )
        self.assertEqual(
            response.url, "https://checkout.stripe.com/replacement"
        )
        self.assertEqual(Order.objects.count(), 2)
        replacement = Order.objects.exclude(pk=old.pk).get()
        self.assertEqual(replacement.total_price, Decimal("21.75"))
        self.assertEqual(replacement.items.get().quantity, 3)
        old.refresh_from_db()
        self.assertEqual(old.stripe_session_id, "cs_test_123")
        self.assertEqual(old.total_price, Decimal("14.50"))

    def test_changed_contact_expiration_failure_preserves_existing_attempt(
        self,
    ):
        old, _ = self.create_order()
        with (
            patch(
                "checkout.views.stripe.checkout.Session.expire",
                side_effect=stripe.APIConnectionError(
                    "expiration unavailable"
                ),
            ),
            patch("checkout.views.stripe.checkout.Session.create") as create,
        ):
            response = self.client.post(
                self.url, {**self.data, "email": "updated@example.test"}
            )
        self.assertContains(response, "could not start payment")
        self.assertEqual(self.retrieve.call_count, 2)
        create.assert_not_called()
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(
            self.client.session["pending_order"], str(old.public_id)
        )
        old.refresh_from_db()
        self.assertEqual(old.email, self.data["email"])
        self.assertEqual(old.stripe_session_id, "cs_test_123")
        self.assertTrue(self.client.session["cart"])

    def test_expiration_racing_completion_waits_for_original_webhook(self):
        old, _ = self.create_order()
        self.retrieve.side_effect = [
            SimpleNamespace(
                id=old.stripe_session_id,
                status="open",
                url="https://checkout.stripe.com/old",
            ),
            SimpleNamespace(
                id=old.stripe_session_id, status="complete", url=None
            ),
        ]
        with (
            patch(
                "checkout.views.stripe.checkout.Session.expire",
                side_effect=stripe.InvalidRequestError(
                    "Session has already completed", param=None
                ),
            ),
            patch("checkout.views.stripe.checkout.Session.create") as create,
        ):
            response = self.client.post(
                self.url, {**self.data, "address": "Updated address"}
            )
        self.assertEqual(
            response.url, reverse("checkout:success", args=[old.public_id])
        )
        create.assert_not_called()
        self.assertEqual(Order.objects.count(), 1)
        old.refresh_from_db()
        self.assertEqual(old.status, "pending")
        self.assertEqual(old.address, self.data["address"])

    def test_lost_expiration_response_can_recover_confirmed_expiry(self):
        old, _ = self.create_order()
        self.retrieve.side_effect = [
            SimpleNamespace(
                id=old.stripe_session_id,
                status="open",
                url="https://checkout.stripe.com/old",
            ),
            SimpleNamespace(
                id=old.stripe_session_id, status="expired", url=None
            ),
        ]
        with (
            patch(
                "checkout.views.stripe.checkout.Session.expire",
                side_effect=stripe.APIConnectionError(
                    "lost expiration response"
                ),
            ),
            patch(
                "checkout.views.stripe.checkout.Session.create",
                return_value=SimpleNamespace(
                    id="cs_replacement",
                    status="open",
                    url="https://checkout.stripe.com/replacement",
                ),
            ) as create,
        ):
            response = self.client.post(
                self.url, {**self.data, "email": "updated@example.test"}
            )
        self.assertEqual(
            response.url, "https://checkout.stripe.com/replacement"
        )
        create.assert_called_once()
        replacement = Order.objects.exclude(pk=old.pk).get()
        self.assertEqual(replacement.email, "updated@example.test")
        old.refresh_from_db()
        self.assertEqual(old.stripe_session_id, "cs_test_123")

    def test_expiration_with_unknown_result_never_starts_replacement(self):
        old, _ = self.create_order()
        self.retrieve.side_effect = [
            SimpleNamespace(
                id=old.stripe_session_id,
                status="open",
                url="https://checkout.stripe.com/old",
            ),
            stripe.APIConnectionError("cannot recover expiration status"),
        ]
        with (
            patch(
                "checkout.views.stripe.checkout.Session.expire",
                side_effect=stripe.APIConnectionError(
                    "lost expiration response"
                ),
            ),
            patch("checkout.views.stripe.checkout.Session.create") as create,
        ):
            response = self.client.post(
                self.url, {**self.data, "address": "Updated address"}
            )
        self.assertContains(response, "could not start payment")
        create.assert_not_called()
        self.assertEqual(Order.objects.count(), 1)
        old.refresh_from_db()
        self.assertEqual(old.stripe_session_id, "cs_test_123")

    def test_changed_contact_recovers_lost_create_response_before_expiring_it(
        self,
    ):
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=stripe.APIConnectionError("lost creation response"),
        ) as first:
            self.client.post(self.url, self.data)
        old = Order.objects.get()
        changed = {**self.data, "email": "updated@example.test"}
        calls = []

        def recover_or_create(**kwargs):
            calls.append("create")
            session_id = "cs_recovered" if len(calls) == 1 else "cs_new"
            return SimpleNamespace(
                id=session_id,
                status="open",
                url=f"https://checkout.stripe.com/{session_id}",
            )

        def expire(*args, **kwargs):
            calls.append("expire")
            return SimpleNamespace(
                id="cs_recovered", status="expired", url=None
            )

        with (
            patch(
                "checkout.views.stripe.checkout.Session.create",
                side_effect=recover_or_create,
            ) as create,
            patch(
                "checkout.views.stripe.checkout.Session.expire",
                side_effect=expire,
            ),
        ):
            response = self.client.post(self.url, changed)
        self.assertEqual(calls, ["create", "expire", "create"])
        self.assertEqual(
            create.call_args_list[0].kwargs, first.call_args.kwargs
        )
        self.assertNotEqual(
            create.call_args_list[0].kwargs["idempotency_key"],
            create.call_args_list[1].kwargs["idempotency_key"],
        )
        self.assertEqual(response.url, "https://checkout.stripe.com/cs_new")
        old.refresh_from_db()
        self.assertEqual(old.stripe_session_id, "cs_recovered")
        replacement = Order.objects.exclude(pk=old.pk).get()
        self.assertEqual(replacement.email, changed["email"])

    def test_changed_cart_with_recovered_completed_session_does_not_pay_again(
        self,
    ):
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=stripe.APIConnectionError("lost creation response"),
        ) as first:
            self.client.post(self.url, self.data)
        old = Order.objects.get()
        session = self.client.session
        session["cart"][str(self.product.pk)] = 3
        session.save()
        with (
            patch(
                "checkout.views.stripe.checkout.Session.create",
                return_value=SimpleNamespace(
                    id="cs_recovered", status="complete", url=None
                ),
            ) as recover,
            patch("checkout.views.stripe.checkout.Session.expire") as expire,
        ):
            response = self.client.post(self.url, self.data)
        self.assertEqual(
            response.url, reverse("checkout:success", args=[old.public_id])
        )
        recover.assert_called_once()
        self.assertEqual(recover.call_args.kwargs, first.call_args.kwargs)
        expire.assert_not_called()
        self.assertEqual(Order.objects.count(), 1)
        old.refresh_from_db()
        self.assertEqual(old.stripe_session_id, "cs_recovered")
        self.assertEqual(old.status, "pending")
        self.assertEqual(old.total_price, Decimal("14.50"))

    def test_same_browser_can_recover_confirmation_list_from_checkout_state(
        self,
    ):
        order, _ = self.create_order()
        session = self.client.session
        session.pop("checkout_orders", None)
        session.pop("pending_order", None)
        session.save()
        url = reverse("checkout:success", args=[order.public_id])
        self.assertContains(
            self.client.get(url), "Awaiting payment confirmation"
        )
        self.assertIn(
            str(order.public_id), self.client.session["checkout_orders"]
        )
        self.assertEqual(Client().get(url).status_code, 404)

    def test_paid_active_order_with_lost_session_list_does_not_charge_again(
        self,
    ):
        order, _ = self.create_order()
        self.webhook(self.event(order))
        session = self.client.session
        session.pop("checkout_orders", None)
        session.pop("pending_order", None)
        session.save()
        with patch("checkout.views.stripe.checkout.Session.create") as create:
            response = self.client.post(self.url, self.data)
        self.assertEqual(
            response.url, reverse("checkout:success", args=[order.public_id])
        )
        create.assert_not_called()
        self.assertEqual(Order.objects.count(), 1)
        self.assertContains(self.client.get(response.url), "Payment confirmed")
        self.assertEqual(self.client.session["cart"], {})

    def test_new_purchase_after_confirmed_cart_clear_starts_fresh_checkout(
        self,
    ):
        old, _ = self.create_order()
        self.webhook(self.event(old))
        self.client.get(reverse("checkout:success", args=[old.public_id]))
        self.client.post(reverse("cart:add_to_cart", args=[self.product.pk]))
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_new_purchase",
                status="open",
                url="https://checkout.stripe.com/new-purchase",
            ),
        ) as create:
            response = self.client.post(self.url, self.data)
        self.assertEqual(
            response.url, "https://checkout.stripe.com/new-purchase"
        )
        self.assertEqual(Order.objects.count(), 2)
        new = Order.objects.exclude(pk=old.pk).get()
        self.assertEqual(new.total_price, Decimal("7.25"))
        self.assertNotEqual(
            create.call_args.kwargs["idempotency_key"],
            f"order-{old.public_id}",
        )

    def test_lost_lease_after_creation_recovers_same_durable_attempt(self):
        competing_token = uuid4()

        def create_after_lease_takeover(**kwargs):
            CheckoutState.objects.update(
                processing_token=competing_token,
                processing_until=timezone.now() + timedelta(seconds=60),
            )
            return SimpleNamespace(
                id="cs_durable",
                status="open",
                url="https://checkout.stripe.com/durable",
            )

        with patch(
            "checkout.views.stripe.checkout.Session.create",
            side_effect=create_after_lease_takeover,
        ) as first:
            response = self.client.post(self.url, self.data)
        self.assertContains(response, "being processed")
        order = Order.objects.get()
        self.assertIsNone(order.stripe_session_id)
        self.assertTrue(order.stripe_checkout_payload)
        state = CheckoutState.objects.get()
        self.assertEqual(state.active_order_id, order.pk)
        self.assertEqual(state.processing_token, competing_token)
        CheckoutState.objects.update(
            processing_until=timezone.now() - timedelta(seconds=1)
        )
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=SimpleNamespace(
                id="cs_durable",
                status="open",
                url="https://checkout.stripe.com/durable",
            ),
        ) as recovered:
            response = self.client.post(self.url, self.data)
        self.assertEqual(response.url, "https://checkout.stripe.com/durable")
        self.assertEqual(first.call_args.kwargs, recovered.call_args.kwargs)
        self.assertEqual(Order.objects.count(), 1)
        order.refresh_from_db()
        self.assertEqual(order.stripe_session_id, "cs_durable")
