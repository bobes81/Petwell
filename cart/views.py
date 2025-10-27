from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product

def view_cart(request):
    """Display the contents of the shopping cart."""
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for item_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=int(item_id))
        total += product.price * quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity
        })

    return render(request, 'cart/cart.html', {'items': items, 'total': total})


def add_to_cart(request, item_id):
    """Add a product to the shopping cart."""
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    cart[item_id] = cart.get(item_id, 0) + 1
    request.session['cart'] = cart
    return redirect('view_cart')


def remove_from_cart(request, item_id):
    """Remove a product from the cart."""
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        del cart[item_id]
    request.session['cart'] = cart
    return redirect('view_cart')
