from django.urls import path

from . import views

app_name = "orders"
urlpatterns = [
    path("", views.history, name="history"),
    path("<uuid:public_id>/reorder/", views.reorder, name="reorder"),
]
