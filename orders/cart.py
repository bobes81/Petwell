from .models import Order


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
    changed = False
    for order in orders:
        for item in order.items.all():
            key = str(item.product_id)
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
        request.session["cleared_orders"] = cleared[-50:]
        if request.session.get("pending_order") in cleared:
            request.session.pop("pending_order", None)
