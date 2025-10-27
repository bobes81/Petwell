from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blog.urls"), name="home"),
    path("account/", include("accounts.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
    path("products/", include("products.urls")),
    re_path(r"^robots\.txt$", serve, {"path": "robots.txt", "document_root": settings.BASE_DIR / 'templates'}),
    re_path(r"^sitemap\.xml$", serve, {"path": "sitemap.xml", "document_root": settings.BASE_DIR / 'templates'}),
]
