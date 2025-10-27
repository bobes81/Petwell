from django.contrib import admin
from django.urls import path, include
from petwell.views import robots_txt, sitemap_xml

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blog.urls")),
    path("account/", include("accounts.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
    path("products/", include("products.urls")),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
]
