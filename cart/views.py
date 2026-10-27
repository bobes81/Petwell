from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from orders.cart import clear_paid_purchases
from products.models import Product


def view_cart(request):
    clear_paid_purchases(request)
    cart = request.session.get("cart", {})
    items = []
    total = 0
    total_quantity = 0

    for product_id, quantity in cart.items():
        product = Product.objects.filter(pk=product_id).first()
        if product is None:
            items.append(
                {
                    "unavailable": True,
                    "product": {
                        "id": product_id,
                        "name": "Unavailable product",
                    },
                    "quantity": quantity,
                    "subtotal": 0,
                }
            )
            continue
        subtotal = product.price * quantity
        total += subtotal
        total_quantity += quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    context = {
        "items": items,
        "total": total,
        "total_quantity": total_quantity,
    }
    return render(request, "cart/cart.html", context)


@require_POST
def add_to_cart(request, product_id):
    clear_paid_purchases(request)
    cart = request.session.get("cart", {})
    get_object_or_404(Product, pk=product_id)
    cart[str(product_id)] = min(cart.get(str(product_id), 0) + 1, 99)
    request.session["cart"] = cart

    product = get_object_or_404(Product, pk=product_id)
    messages.success(request, f"🛒 '{product.name}' added to your cart!")
    return redirect("products:product_list")


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session["cart"] = cart
        messages.info(request, "❌ Item removed from cart.")
    return redirect("cart:view_cart")
