from django.shortcuts import render

def checkout_success(request):
    """Simple checkout success page."""
    return render(request, 'checkout/checkout_success.html')
