from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
import stripe

def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('view_cart')

    total = sum([10 * int(qty) for qty in cart.values()])  # placeholder prices

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'gbp',
                'product_data': {'name': 'PetWell Order'},
                'unit_amount': total * 100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://petwell-app-ivo-59ea39e413cf.herokuapp.com/checkout/success/',
        cancel_url='https://petwell-app-ivo-59ea39e413cf.herokuapp.com/cart/',
    )
    return redirect(session.url, code=303)

def checkout_success(request):
    """Clear the cart and thank the user."""
    if request.session.get('cart'):
        request.session['cart'] = {}
        if request.user.is_authenticated and request.user.email:
            send_mail(
                'PetWell Order Confirmation',
                'Thank you for your purchase! ❤️',
                'petwell@example.com',
                [request.user.email],
                fail_silently=True,
            )
    return render(request, 'checkout/checkout_success.html')
