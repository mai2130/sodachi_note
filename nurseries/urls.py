from django.urls import path
from .views import NurseryMyPageView

app_name = 'nurseries'

urlpatterns = [
    path('', NurseryMyPageView.as_view(), name='mypage'),
]
