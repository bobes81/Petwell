def cart_item_count(request):
    cart = request.session.get("cart", {})
    quantities = cart.values() if isinstance(cart, dict) else []
    return {
        "cart_item_count": sum(
            q for q in quantities if type(q) is int and 1 <= q <= 99
        )
    }
