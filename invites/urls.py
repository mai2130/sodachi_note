from django.urls import path
from .views import AccountListView, AccountManageView

app_name = 'invites'

urlpatterns = [
    path('accounts/', AccountListView.as_view(), name='account_list'),
    path('accounts/<int:pk>/', AccountManageView.as_view(), name='account_manage'),
]
