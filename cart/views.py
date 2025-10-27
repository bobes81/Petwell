from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product

def view_cart(request):
    """Display all cart items and total."""
    cart = request.session.get('cart', {})
    items = []
    total = 0
    total_quantity = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal
        total_quantity += quantity

    context = {
        'items': items,
        'total': round(total, 2),
        'total_quantity': total_quantity,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, product_id):
    """Add one product to cart."""
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart:view_cart')


def remove_from_cart(request, product_id):
    """Remove product from cart."""
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart:view_cart')
