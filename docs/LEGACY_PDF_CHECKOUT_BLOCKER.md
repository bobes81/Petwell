# Checkout blocker review — legacy undeliverable PDF (29 Oct 2026)

Read-only code review of branch `fix/pp5-resubmission`. **No production data or payment settings were changed.**

## Confirmed gap

The existing Product model has no `is_active`/`available` field. `products.views.product_list` returns `Product.objects.all()`; `cart.views.add_to_cart` accepts any existing product ID; `orders.views.reorder` accepts products with positive prices; `checkout.views.cart_products` validates existence and positive price but not fulfilment availability. Consequently, an existing `Mindful Pet Journal (PDF)` with a positive price could still be sold even if omitted from future seeding. An old cart or a Buy Again action can reach checkout. Hiding the shop card alone is not a fix.

## Proposed minimal tested change (NOT yet implemented)

- Add a backward-compatible Product availability flag with a reviewed migration and safe default for existing physical products; explicitly identify and archive only the undeliverable legacy PDF after verifying the actual production record.
- Filter unavailable products from the public catalogue.
- Reject direct add-to-cart of unavailable products.
- Keep unavailable existing-cart lines visible as unavailable and exclude them from payable totals; require their removal before checkout.
- Exclude unavailable items from Buy Again, while preserving historical OrderItem records and paid-order visibility.
- Reject unavailable products in checkout cart validation and test pending/active Stripe Sessions against the withdrawal policy. Do not blindly expire or mark historical payments paid.
- Add targeted regression tests for catalogue, direct POST, stale cart, reorder, checkout, and order history.
- Rehearse migrations on a disposable database and check the real production schema before any release. A fresh backup and explicit approval are mandatory before production migration or archive.
- Do not enable Stripe live or sandbox payments for customer-facing checkout until the legacy offer is resolved and a sandbox webhook payment has been verified.

## Evidence reviewed

`products/models.py`, `products/views.py`, `cart/views.py`, `orders/views.py`, `checkout/views.py` at the PR branch as of this review. This is a code-path finding, **not** proof of the current production PDF record's price or presence. No credentials or private feedback were published.

This note is a handoff for an implementation/test task; it does not claim the blocker is fixed.
