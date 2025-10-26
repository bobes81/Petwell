from django.shortcuts import render

def product_list(request):
    """Simple test view for products."""
    return render(request, 'products/product_list.html')
