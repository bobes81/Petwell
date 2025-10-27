from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('checkout/', include(('checkout.urls', 'checkout'), namespace='checkout')),
    path('accounts/', include('allauth.urls')),
]
