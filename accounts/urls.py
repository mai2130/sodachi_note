from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import EmailLoginView, FacilitySignUpView

app_name = 'accounts'

urlpatterns = [
    path('login/', EmailLoginView.as_view(), name='login'),
    path('signup/facility/', FacilitySignUpView.as_view(), name='signup_facility'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
