from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import EmailLoginView, FacilitySignUpView, GuardianSignUpView, ChildMyPageView

app_name = 'accounts'

urlpatterns = [
    path('login/', EmailLoginView.as_view(), name='login'),
    path('signup/facility/', FacilitySignUpView.as_view(), name='signup_facility'),
    path('signup/guardian/', GuardianSignUpView.as_view(), name='signup_guardian'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("child/mypage/", ChildMyPageView.as_view(), name="child_mypage"),
]
