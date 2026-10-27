from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Order


@login_required
def history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related(
        "items__product"
    )
    return render(request, "orders/history.html", {"orders": orders})


@login_required
@require_POST
def reorder(request, public_id):
    order = get_object_or_404(
        Order, public_id=public_id, user=request.user, status="paid"
    )
    cart = request.session.get("cart", {}).copy()
    for item in order.items.select_related("product"):
        if item.product.price > 0:
            key = str(item.product_id)
            cart[key] = min(cart.get(key, 0) + item.quantity, 99)
    request.session["cart"] = cart
    messages.success(
        request,
        "Available items added to your cart at current prices. "
        "Review before paying.",
    )
    return redirect("cart:view_cart")
