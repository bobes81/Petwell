from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product

def view_cart(request):
    """Display the contents of the shopping cart."""
    cart = request.session.get('cart', {})
    products = []
    total = 0
    for item_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=item_id)
        subtotal = product.price * quantity
        products.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        total += subtotal
    context = {'cart_items': products, 'total': total}
    return render(request, 'cart/cart.html', context)

def add_to_cart(request, item_id):
    """Add a product to the cart."""
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + quantity
    request.session['cart'] = cart
    return redirect('view_cart')

def remove_from_cart(request, item_id):
    """Remove a product from the cart."""
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
    request.session['cart'] = cart
    return redirect('view_cart')
