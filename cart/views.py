from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product

def view_cart(request):
    """Display all items in the cart."""
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')
    total_quantity = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        total_quantity += quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': round(subtotal, 2),
        })

    context = {
        'items': items,
        'total': round(total, 2),
        'total_quantity': total_quantity,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, product_id):
    """Add one product to cart."""
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    request.session['cart'] = cart
    return redirect('cart:view_cart')


def remove_from_cart(request, product_id):
    """Remove product from cart."""
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    return redirect('cart:view_cart')
