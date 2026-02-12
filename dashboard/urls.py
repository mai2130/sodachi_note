from django.urls import path
from .views import HomeView #, GuardianHomeView

app_name = "dashboard"

urlpatterns = [
    path("",HomeView.as_view(),name="home"),
]

