from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings

def checkout(request):
    """Simple checkout page with confirmation email."""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        send_mail(
            subject="Your PetWell Order Confirmation",
            message=f"Thank you, {name}! Your order will be shipped to:\n\n{address}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email, settings.DEFAULT_FROM_EMAIL],
        )
        return render(request, "checkout/success.html", {"name": name, "email": email})
    return render(request, "checkout/checkout.html")
