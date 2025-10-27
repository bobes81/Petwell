app_name = "checkout"
from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
]
