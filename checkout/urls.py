from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout_success, name='checkout_success'),
]
