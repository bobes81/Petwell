from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product

def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    total_quantity = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        subtotal = product.price * quantity
        total += subtotal
        total_quantity += quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    context = {'items': items, 'total': total, 'total_quantity': total_quantity}
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart

    product = get_object_or_404(Product, pk=product_id)
    messages.success(request, f"🛒 '{product.name}' added to your cart!")
    return redirect('products:product_list')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.info(request, "❌ Item removed from cart.")
    return redirect('cart:view_cart')
