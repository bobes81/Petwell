from uuid import uuid4

from .models import Order


def cart_line_tokens(request):
    """Give each continuous cart line an identity, reset on remove/re-add."""
    previous = request.session.get("cart_line_tokens", {})
    tokens = {
        key: previous.get(key) or str(uuid4())
        for key in request.session.get("cart", {})
    }
    if tokens != previous:
        request.session["cart_line_tokens"] = tokens
    return tokens


def clear_paid_purchases(request):
    owned = request.session.get("checkout_orders", [])
    cleared = request.session.get("cleared_orders", [])
    ids = [key for key in owned if key not in cleared]
    if not ids:
        return
    orders = Order.objects.filter(
        public_id__in=ids, status="paid"
    ).prefetch_related("items")
    cart = request.session.get("cart", {}).copy()
    tokens = cart_line_tokens(request)
    changed = False
    for order in orders:
        for item in order.items.all():
            key = str(item.product_id)
            # Legacy orders have no line identity: keep the cart rather than
            # risk removing new items based on an unprovable association.
            if not tokens.get(key) or tokens[
                key
            ] != order.cart_line_tokens.get(key):
                continue
            quantity = cart.get(key, 0)
            remaining = (
                quantity - item.quantity if type(quantity) is int else 0
            )
            if remaining > 0:
                cart[key] = remaining
            else:
                cart.pop(key, None)
        cleared.append(str(order.public_id))
        changed = True
    if changed:
        request.session["cart"] = cart
        cart_line_tokens(request)
        request.session["cleared_orders"] = cleared[-50:]
        if request.session.get("pending_order") in cleared:
            request.session.pop("pending_order", None)
