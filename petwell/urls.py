from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView


def public_sitemap(request):
    from django.shortcuts import render

    from blog.models import BlogPost

    return render(
        request,
        "sitemap.xml",
        {"site_url": settings.SITE_URL, "posts": BlogPost.objects.all()},
        content_type="application/xml",
    )


urlpatterns = [
    path("orders/", include("orders.urls")),
    path("admin/", admin.site.urls),
    # --- Main homepage ---
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    # --- Products ---
    path(
        "products/",
        include(("products.urls", "products"), namespace="products"),
    ),
    # --- Blog, Cart, Checkout, Accounts ---
    path("blog/", include(("blog.urls", "blog"), namespace="blog")),
    path("cart/", include(("cart.urls", "cart"), namespace="cart")),
    path(
        "checkout/",
        include(("checkout.urls", "checkout"), namespace="checkout"),
    ),
    path("accounts/", include("allauth.urls")),
]

# --- Robots.txt and Sitemap.xml ---
urlpatterns += [
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain",
            extra_context={"site_url": settings.SITE_URL},
        ),
        name="robots",
    ),
    path(
        "sitemap.xml",
        public_sitemap,
        name="sitemap",
    ),
]
