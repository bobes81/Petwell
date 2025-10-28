from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Main homepage ---
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    # --- Products ---
    path('products/', include(('products.urls', 'products'), namespace='products')),

    # --- Blog, Cart, Checkout, Accounts ---
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('checkout/', include(('checkout.urls', 'checkout'), namespace='checkout')),
    path('accounts/', include('allauth.urls')),
]

# --- Robots.txt and Sitemap.xml ---
urlpatterns += [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
    path(
        "sitemap.xml",
        TemplateView.as_view(template_name="sitemap.xml", content_type="application/xml"),
        name="sitemap",
    ),
]