from django.urls import path
from . import views

app_name = "families"

urlpatterns = [
    path("info/", views.family_info, name="info"),
    path("info/<int:pk>/confirm/", views.family_confirm, name="confirm"),
    path("info/<int:pk>/delete/", views.family_delete, name="delete"),
]