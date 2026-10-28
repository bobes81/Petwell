from django.urls import path

from . import views

app_name = "pets"
urlpatterns = [
    path("", views.pet_list, name="list"),
    path("new/", views.pet_create, name="create"),
    path("<int:pk>/edit/", views.pet_edit, name="edit"),
    path("<int:pk>/delete/", views.pet_delete, name="delete"),
]
