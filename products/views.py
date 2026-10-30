from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

def product_list(request):
    products = Product.objects.filter(is_available=True, price__gt=0)
    return render(request, "products/product_list.html", {"products": products})
