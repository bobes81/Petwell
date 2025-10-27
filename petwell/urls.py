from blog.views_home import home
from blog.home_view import home
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", home, name="home"),
    path("", home, name="home"),
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
    path('account/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),  # important as this adds login/logout/signup
    path('cart/', include('cart.urls')),
    path('checkout/', include('checkout.urls')),
    path('products/', include('products.urls')),
]
