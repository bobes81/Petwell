cat > petwell/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls'), name='home'),
    path('account/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('checkout/', include('checkout.urls')),
    path('products/', include('products.urls')),
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain'
        ),
    ),
    path(
        'sitemap.xml',
        TemplateView.as_view(
            template_name='sitemap.xml',
            content_type='application/xml'
        ),
    ),
]
EOF