from django.urls import path # path("URLの形", 動かすView, name="名前")
from .views import AccountListView, AccountManageView, AccountCreateView

app_name = 'invites'

urlpatterns = [
    path('accounts/', AccountListView.as_view(), name='account_list'), # 一覧画面
    path('accounts/new/', AccountCreateView.as_view(), name='account_new'), # 新規作成画面
    path('accounts/<int:pk>/', AccountManageView.as_view(), name='account_manage'), # 編集画面
]
