"""Review one legacy offer, with an explicit guarded withdrawal option."""

import hashlib
import json
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count, Q, Sum, TextField
from django.db.models.functions import Cast
from django.utils import timezone

from orders.models import CheckoutState, Order, OrderItem
from products.models import Product


LEGACY_NAME = "Mindful Pet Journal (PDF)"


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _products():
    # Preserve the exact stored reference, including version and NULL/empty
    # distinction. str(CloudinaryResource) would omit version information.
    return Product.objects.annotate(
        review_image_reference=Cast("image", output_field=TextField())
    )


def _material(product):
    return {
        "product_id": product.pk,
        "name": product.name,
        "description": product.description,
        "price": format(product.price, ".2f"),
        "image_reference": product.review_image_reference,
    }


def _fingerprint(material):
    # Availability is deliberately excluded so the same reviewed operation
    # remains a no-op on repetition rather than reactivating or changing data.
    return _digest(json.dumps(material, sort_keys=True, separators=(",", ":")))


def _review(product):
    material = _material(product)
    orders = Order.objects.filter(items__product_id=product.pk)
    has_session = Q(stripe_session_id__isnull=False) & ~Q(stripe_session_id="")
    counts = orders.aggregate(
        orders=Count("pk", distinct=True),
        pending=Count("pk", filter=Q(status="pending"), distinct=True),
        paid=Count("pk", filter=Q(status="paid"), distinct=True),
        with_session=Count("pk", filter=has_session, distinct=True),
        unmapped_with_payload=Count(
            "pk", filter=~has_session & ~Q(stripe_checkout_payload={}),
            distinct=True,
        ),
    )
    counts.update(OrderItem.objects.filter(product_id=product.pk).aggregate(
        item_rows=Count("pk"), purchased_quantity=Sum("quantity", default=0)
    ))
    counts["active_checkout_leases"] = CheckoutState.objects.filter(
        active_order__items__product_id=product.pk,
        processing_token__isnull=False,
        processing_until__gt=timezone.now(),
    ).distinct().count()
    return {
        "product_id": product.pk,
        "name": product.name,
        "price": material["price"],
        "is_available": product.is_available,
        "description_sha256": _digest(product.description),
        "image_present": bool(material["image_reference"]),
        "image_reference_sha256": _digest(json.dumps(material["image_reference"])),
        "snapshot_fingerprint": _fingerprint(material),
        "history_counts": counts,
    }


class Command(BaseCommand):
    help = (
        "Review exact-name legacy PDF candidates without writing by default. "
        "--apply requires an explicit ID, reviewed fingerprint and owner attestations."
    )

    def add_arguments(self, parser):
        parser.add_argument("--product-id", type=int)
        parser.add_argument("--expected-fingerprint")
        parser.add_argument("--confirm-undeliverable", action="store_true")
        parser.add_argument("--checkout-paused", action="store_true")
        parser.add_argument("--orders-reviewed", action="store_true")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        product_id = options["product_id"]
        expected = options["expected_fingerprint"]
        if product_id is not None and (
            type(product_id) is not int or not 0 < product_id <= 9223372036854775807
        ):
            raise CommandError("Use a valid positive product ID; do not guess it.")
        if expected is not None and (
            not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected)
        ):
            raise CommandError("Use the complete SHA-256 fingerprint from the private review.")
        attestations = {
            "undeliverable_confirmed": options["confirm_undeliverable"],
            "checkout_paused_and_drained": options["checkout_paused"],
            "orders_and_provider_reviewed": options["orders_reviewed"],
        }
        if options["apply"] and (
            product_id is None or expected is None or not all(attestations.values())
        ):
            raise CommandError(
                "Application requires --product-id, --expected-fingerprint, "
                "--confirm-undeliverable, --checkout-paused and --orders-reviewed. "
                "These flags are owner attestations, not evidence of provider state."
            )
        mode = "DRY_RUN"
        if options["apply"]:
            with transaction.atomic():
                product = _products().select_for_update().filter(pk=product_id).first()
                self._identity(product)
                material = _material(product)
                if _fingerprint(material) != expected:
                    raise CommandError("The product changed since review; obtain a new private review.")
                report = _review(product)
                if product.is_available:
                    if report["history_counts"]["active_checkout_leases"]:
                        raise CommandError(
                            "An active checkout lease remains. Stop and drain requests "
                            "and reconcile provider state before withdrawal."
                        )
                    changed = _products().filter(
                        pk=product.pk, name=LEGACY_NAME, is_available=True,
                        description=product.description, price=product.price,
                        review_image_reference=product.review_image_reference,
                    ).update(is_available=False)
                    if changed != 1:
                        raise CommandError("The product changed during application; no withdrawal was saved.")
                    report["is_available"] = False
                    mode = "APPLIED"
                else:
                    mode = "ALREADY_WITHDRAWN"
            candidates = [report]
        else:
            query = _products().filter(name=LEGACY_NAME).order_by("pk")
            if product_id is not None:
                query = query.filter(pk=product_id)
            products = list(query[:21])
            if len(products) > 20:
                raise CommandError("More than 20 exact-name candidates; review them privately in admin.")
            if product_id is not None:
                self._identity(products[0] if products else None)
            candidates = [_review(product) for product in products]
            if expected is not None and (
                len(candidates) != 1 or candidates[0]["snapshot_fingerprint"] != expected
            ):
                raise CommandError("The selected product fingerprint does not match the private review.")
        self.stdout.write(json.dumps({
            "mode": mode,
            "candidate_count": len(candidates),
            "ambiguous": len(candidates) > 1,
            "candidates": candidates,
            "owner_attestations": attestations,
            "limitations": [
                "Use only after the reviewed migrations on the intended database.",
                "Review actual description and image privately in admin; hashes are not proof of identity or rights.",
                "Flags record owner attestations only. No provider state was verified or changed.",
                "Withdrawal does not expire hosted Sessions, fulfil/refund orders or delete history.",
                "No customer, order UUID or Stripe identifiers are included. Keep the record review private.",
            ],
        }, indent=2))

    @staticmethod
    def _identity(product):
        if product is None or product.name != LEGACY_NAME:
            raise CommandError("The explicit ID does not identify the exact legacy PDF name. Nothing was changed.")
