def cart_item_count(request):
    cart = request.session.get('cart', {})
    total_quantity = sum(cart.values()) if cart else 0
    return {'cart_item_count': total_quantity}
