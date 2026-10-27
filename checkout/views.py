import logging
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

from orders.cart import clear_paid_purchases
from orders.models import Order, OrderItem
from products.models import Product

from .forms import CheckoutForm

logger = logging.getLogger(__name__)


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
        if product.price <= 0:
            raise ValueError(
                "A product price is unavailable. Please contact the shop."
            )
        items.append((product, quantity))
    return items


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
        if not settings.STRIPE_SECRET_KEY or (
            settings.STRIPE_SECRET_KEY.startswith(("sk_live_", "rk_live_"))
            != settings.STRIPE_LIVE_MODE
        ):
            form.add_error(
                None,
                "Payments are temporarily unavailable. "
                "Your cart has been kept.",
            )
        else:
            # Repeated submissions reuse the pending order
            # and its Stripe idempotency key.
            order = (
                Order.objects.filter(
                    public_id=request.session.get("pending_order"),
                    status="pending",
                ).first()
                if request.session.get("pending_order")
                else None
            )
            snapshot = sorted((p.pk, q, p.price) for p, q in items)
            if order and (
                order.full_name != form.cleaned_data["name"]
                or order.email != form.cleaned_data["email"]
                or order.address != form.cleaned_data["address"]
                or sorted(
                    order.items.values_list("product_id", "quantity", "price")
                )
                != snapshot
            ):
                order = None
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
                    )
                    OrderItem.objects.bulk_create(
                        [
                            OrderItem(
                                order=order,
                                product=p,
                                quantity=q,
                                price=p.price,
                            )
                            for p, q in items
                        ]
                    )
            request.session["pending_order"] = str(order.public_id)
            owned = request.session.get("checkout_orders", [])
            if str(order.public_id) not in owned:
                request.session["checkout_orders"] = (
                    owned + [str(order.public_id)]
                )[-50:]
            try:
                session = stripe.checkout.Session.create(
                    api_key=settings.STRIPE_SECRET_KEY,
                    idempotency_key=f"order-{order.public_id}",
                    mode="payment",
                    payment_method_types=["card"],
                    client_reference_id=str(order.public_id),
                    metadata={"order_id": str(order.public_id)},
                    customer_email=order.email,
                    line_items=[
                        {
                            "price_data": {
                                "currency": "gbp",
                                "product_data": {"name": p.name},
                                "unit_amount": int(p.price * 100),
                            },
                            "quantity": q,
                        }
                        for p, q in items
                    ],
                    success_url=settings.SITE_URL
                    + reverse("checkout:success", args=[order.public_id]),
                    cancel_url=settings.SITE_URL
                    + reverse("checkout:checkout"),
                )
                order.stripe_session_id = session.id
                order.save(update_fields=["stripe_session_id"])
                return redirect(session.url)
            except stripe.StripeError:
                logger.warning(
                    "Stripe checkout creation failed for order %s",
                    order.public_id,
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
    if str(public_id) not in request.session.get("checkout_orders", []):
        return HttpResponse(status=404)
    order = get_object_or_404(Order, public_id=public_id)
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
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponseBadRequest("Invalid webhook")
    if event["type"] not in (
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    ):
        return HttpResponse(status=200)
    session = event["data"]["object"]
    if session.get("payment_status") != "paid":
        return HttpResponse(status=200)
    if not session.get("id"):
        return HttpResponseBadRequest("Missing session")
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
            or session.get("metadata", {}).get("order_id")
            != str(order.public_id)
            or session.get("client_reference_id") != str(order.public_id)
            or bool(session.get("livemode")) != settings.STRIPE_LIVE_MODE
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
