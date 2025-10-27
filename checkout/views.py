from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from products.models import Product
from orders.models import Order, OrderItem

def checkout(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        cart = request.session.get('cart', {})

        total = 0
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=name,
            email=email,
            address=address,
            total_price=0
        )

        for item_id, quantity in cart.items():
            product = Product.objects.get(pk=item_id)
            subtotal = product.price * quantity
            total += subtotal
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        order.total_price = total
        order.save()

        # === HTML email for customer ===
        html_customer = render_to_string(
            "emails/order_confirmation.html",
            {
                "name": name,
                "address": address,
                "total": total,
                "current_year": timezone.now().year,
            },
        )

        send_mail(
            "Your PetWell Order Confirmation",
            f"Thank you, {name}! Your order will be shipped to:\n{address}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_customer,
            fail_silently=False,
        )

        # === Admin notification ===
        html_admin = render_to_string(
            "emails/admin_notification.html",
            {
                "name": name,
                "email": email,
                "address": address,
                "total": total,
            },
        )

        send_mail(
            f"New Petwell Order from {name}",
            f"New order from {name}, total £{total}.",
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            html_message=html_admin,
            fail_silently=False,
        )

        request.session['cart'] = {}
        return render(request, "checkout/success.html", {"name": name, "email": email})

    return render(request, "checkout/checkout.html")
