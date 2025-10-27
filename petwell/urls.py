from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('account/', include('allauth.urls')),
    path('cart/', include('cart.urls')),
    path('checkout/', include('checkout.urls')),
    path('products/', include('products.urls')),
]
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings
from django.urls import re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blog.urls"), name="home"),
    path("account/", include("accounts.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
    path("products/", include("products.urls")),
]

# Serve robots.txt and sitemap.xml from static/
urlpatterns += [
    re_path(r"^robots\.txt$", serve, {"path": "robots.txt", "document_root": settings.STATIC_ROOT}),
    re_path(r"^sitemap\.xml$", serve, {"path": "sitemap.xml", "document_root": settings.STATIC_ROOT}),
]