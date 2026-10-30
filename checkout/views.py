import logging
from datetime import timedelta
from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.cart import cart_line_tokens, clear_paid_purchases
from orders.models import CheckoutState, Order, OrderItem
from products.models import Product

from .coordination import CheckoutBusy, checkout_lease, session_digest
from .forms import CheckoutForm

logger = logging.getLogger(__name__)
UNMAPPED_RETRY_WINDOW = timedelta(hours=23)


def cart_products(cart):
    """Reject stale or invalid carts; prices always come from the database."""
    if not isinstance(cart, dict) or not cart or len(cart) > 100:
        raise ValueError(
            "Your cart is empty or invalid. Please update it before paying."
        )
    items = []
    for key, quantity in cart.items():
        if (
            not str(key).isdigit()
            or type(quantity) is not int
            or not 1 <= quantity <= 99
        ):
            raise ValueError("Invalid cart quantity. Please update your cart.")
        try:
            product = Product.objects.get(pk=key)
        except Product.DoesNotExist:
            raise ValueError(
                "A product is no longer available. "
                "Please remove it from your cart."
            )
        if not product.is_available:
            raise ValueError(
                'A product is no longer available. Please remove it from your cart.'
            )
        if product.price <= 0:
            raise ValueError(
                "A product price is unavailable. Please contact the shop."
            )
        items.append((product, quantity))
    return items


def session_payload(order, items):
    """Freeze every Stripe create parameter; never include secrets in this JSON."""
    return {
        "mode": "payment",
        "payment_method_types": ["card"],
        "client_reference_id": str(order.public_id),
        "metadata": {"order_id": str(order.public_id)},
        "customer_email": order.email,
        "line_items": [
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {"name": product.name},
                    "unit_amount": int(product.price * 100),
                },
                "quantity": quantity,
            }
            for product, quantity in sorted(items, key=lambda item: item[0].pk)
        ],
        "success_url": settings.SITE_URL
        + reverse("checkout:success", args=[order.public_id]),
        "cancel_url": settings.SITE_URL + reverse("checkout:checkout"),
    }


def expire_checkout_session(session, lease):
    """Do not replace a payable attempt until Stripe confirms its end state."""
    lease.assert_current()
    try:
        return stripe.checkout.Session.expire(
            session.id, api_key=settings.STRIPE_SECRET_KEY
        )
    except stripe.StripeError:
        # Expiration can race a completed payment or succeed despite a lost
        # response. Only an authoritative terminal state permits progress.
        lease.assert_current()
        recovered = stripe.checkout.Session.retrieve(
            session.id, api_key=settings.STRIPE_SECRET_KEY
        )
        if recovered.status not in ("complete", "expired"):
            raise
        return recovered


def remember_checkout(request, order):
    """Keep browser confirmation access even after a stale session response."""
    owned = request.session.get("checkout_orders", [])
    if str(order.public_id) not in owned:
        request.session["checkout_orders"] = (owned + [str(order.public_id)])[
            -50:
        ]


def start_checkout(request, form, items, total, tokens, lease):
    """Resolve the browser's durable active attempt before starting another."""
    order = lease.active_order
    if order and order.status == "paid":
        if str(order.public_id) not in request.session.get(
            "cleared_orders", []
        ):
            remember_checkout(request, order)
            return redirect("checkout:success", public_id=order.public_id)
        order = None
    # A legacy attempt without a saved response or payload cannot be retried
    # safely after product labels/URLs have changed.
    if (
        order
        and not order.stripe_session_id
        and not order.stripe_checkout_payload
    ):
        order = None
    snapshot = sorted((p.pk, q, p.price) for p, q in items)
    changed = order is not None and (
        order.full_name != form.cleaned_data["name"]
        or order.email != form.cleaned_data["email"]
        or order.address != form.cleaned_data["address"]
        or (order.cart_line_tokens and order.cart_line_tokens != tokens)
        or sorted(order.items.values_list("product_id", "quantity", "price"))
        != snapshot
    )
    # One renewal handles an expired or superseded Session, including recovery
    # after an earlier connection loss.
    for _ in range(2):
        if order is None:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user
                    if request.user.is_authenticated
                    else None,
                    full_name=form.cleaned_data["name"],
                    email=form.cleaned_data["email"],
                    address=form.cleaned_data["address"],
                    total_price=total,
                    cart_line_tokens=tokens,
                )
                OrderItem.objects.bulk_create(
                    [
                        OrderItem(
                            order=order, product=p, quantity=q, price=p.price
                        )
                        for p, q in items
                    ]
                )
                order.stripe_checkout_payload = session_payload(order, items)
                order.save(update_fields=["stripe_checkout_payload"])
                # Commit the active pointer and immutable request before any
                # Stripe I/O so another worker recovers this same attempt.
                lease.set_order(order)
            changed = False
        request.session["pending_order"] = str(order.public_id)
        remember_checkout(request, order)
        lease.assert_current()
        if order.stripe_session_id:
            session = stripe.checkout.Session.retrieve(
                order.stripe_session_id,
                api_key=settings.STRIPE_SECRET_KEY,
            )
        else:
            # Stripe may prune idempotency keys after 24 hours. An unmapped
            # Session might already have been paid while its webhooks retried.
            # Leave a margin before that retention boundary; never risk creating
            # a second payable Session because the original response was lost.
            if order.created_at <= timezone.now() - UNMAPPED_RETRY_WINDOW:
                form.add_error(
                    None,
                    "This payment attempt needs review before you can retry. "
                    "Your cart has been kept. Please contact the shop.",
                )
                return None
            # Recover an ambiguous create response before replacing it, even
            # if the customer has since changed their cart or contact details.
            session = stripe.checkout.Session.create(
                api_key=settings.STRIPE_SECRET_KEY,
                idempotency_key=f"order-{order.public_id}",
                **order.stripe_checkout_payload,
            )
            lease.assert_current()
            order.stripe_session_id = session.id
            order.save(update_fields=["stripe_session_id"])
        lease.assert_current()
        if session.status == "open" and changed:
            session = expire_checkout_session(session, lease)
            lease.assert_current()
        if session.status == "expired":
            # Keep the old order/Session mapping for late webhooks.
            order = None
            continue
        if session.status == "complete":
            # Changed data must not create another payment while this Session
            # awaits the signed webhook that confirms its result.
            return redirect("checkout:success", public_id=order.public_id)
        if session.status == "open" and session.url and not changed:
            return redirect(session.url)
        break
    form.add_error(
        None,
        "This payment session is unavailable. "
        "Please retry; your cart has been kept.",
    )
    return None


def checkout(request):
    clear_paid_purchases(request)
    form = CheckoutForm(request.POST if request.method == "POST" else None)
    cart = request.session.get("cart", {})
    try:
        items = cart_products(cart)
    except ValueError as exc:
        return render(
            request,
            "checkout/checkout.html",
            {"form": form, "cart_error": str(exc)},
            status=400 if request.method == "POST" else 200,
        )
    total = sum((p.price * q for p, q in items), Decimal("0.00"))
    if request.method == "POST" and form.is_valid():
        if (
            not settings.STRIPE_SECRET_KEY
            or not settings.STRIPE_WEBHOOK_SECRET
            or settings.STRIPE_SECRET_KEY.startswith(("sk_live_", "rk_live_"))
            != settings.STRIPE_LIVE_MODE
        ):
            form.add_error(
                None,
                "Payments are temporarily unavailable. "
                "Your cart has been kept.",
            )
        else:
            lease = None
            try:
                with checkout_lease(request) as lease:
                    response = start_checkout(
                        request,
                        form,
                        items,
                        total,
                        cart_line_tokens(request),
                        lease,
                    )
                    if response is not None:
                        return response
            except CheckoutBusy:
                form.add_error(
                    None,
                    "A payment request is already being processed. "
                    "Please wait and retry; your cart has been kept.",
                )
            except stripe.StripeError:
                logger.warning(
                    "Stripe checkout failed for order %s",
                    getattr(
                        getattr(lease, "active_order", None), "public_id", None
                    ),
                )
                form.add_error(
                    None,
                    "We could not start payment. "
                    "Please retry; your cart has been kept.",
                )
    return render(
        request, "checkout/checkout.html", {"form": form, "total": total}
    )


def success(request, public_id):
    # A return URL is not payment evidence.
    # Only the signed webhook changes status.
    order = get_object_or_404(Order, public_id=public_id)
    owned = str(public_id) in request.session.get("checkout_orders", [])
    if not owned and request.session.session_key:
        # Concurrent SessionMiddleware saves can lose a confirmation list.
        # The durable pointer is scoped to this same unguessable browser key.
        owned = CheckoutState.objects.filter(
            pk=session_digest(request),
            active_order=order,
        ).exists()
    if not owned:
        return HttpResponse(status=404)
    remember_checkout(request, order)
    clear_paid_purchases(request)
    return render(request, "checkout/success.html", {"order": order})


@csrf_exempt
@require_POST
def webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse(status=503)
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.headers.get("Stripe-Signature", ""),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (
        ValueError,
        TypeError,
        AttributeError,
        stripe.SignatureVerificationError,
    ):
        return HttpResponseBadRequest("Invalid webhook")
    try:
        event_type = event["type"]
        if not isinstance(event_type, str):
            return HttpResponseBadRequest("Invalid event type")
        if event_type not in (
            "checkout.session.completed",
            "checkout.session.async_payment_succeeded",
        ):
            return HttpResponse(status=200)
        session = event["data"]["object"]
        if session.get("payment_status") != "paid":
            return HttpResponse(status=200)
        if not session.get("id"):
            return HttpResponseBadRequest("Missing session")
        metadata = session.get("metadata") or {}
        order_reference = metadata.get("order_id")
    except (KeyError, TypeError, AttributeError):
        return HttpResponseBadRequest("Invalid payment event")
    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .filter(stripe_session_id=session.get("id"))
            .first()
        )
        if order is None:
            # Stripe can deliver before the session response is saved.
            # Request a later retry.
            return HttpResponse(status=503)
        if (
            session.get("mode") != "payment"
            or session.get("currency") != "gbp"
            or session.get("amount_total") != int(order.total_price * 100)
            or order_reference != str(order.public_id)
            or session.get("client_reference_id") != str(order.public_id)
            or session.get("livemode") is not settings.STRIPE_LIVE_MODE
        ):
            logger.warning(
                "Payment details mismatch for order %s", order.public_id
            )
            return HttpResponseBadRequest("Payment details mismatch")
        if order.status != "paid":
            order.status = "paid"
            order.paid_at = timezone.now()
            order.save(update_fields=["status", "paid_at"])
    return HttpResponse(status=200)
