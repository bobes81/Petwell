from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product

def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        subtotal = product.price * quantity
        items.append({'product': product, 'quantity': quantity, 'total': subtotal})
        total += subtotal

    return render(request, 'cart/cart.html', {'items': items, 'total': total})


def add_to_cart(request, product_id):
    """Add product to cart session"""
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart:view_cart')


def remove_from_cart(request, product_id):
    """Remove product from cart session"""
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart:view_cart')
