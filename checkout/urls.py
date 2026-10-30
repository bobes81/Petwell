from django.urls import path

from . import views

app_name = "checkout"
urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("success/<uuid:public_id>/", views.success, name="success"),
    path("webhook/", views.webhook, name="webhook"),
]
