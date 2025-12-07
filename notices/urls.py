from django.urls import path
from .views import (
    NoticeListView,
    NoticeDetailView,
    NoticeCreateView,
    NoticeUpdateView,
)

app_name = 'notices'

urlpatterns = [
    path('',NoticeListView.as_view(), name='list'), #一覧ページ
    path('create/', NoticeCreateView.as_view(), name='create'), #新規投稿ページ
    path('<int:pk>/', NoticeDetailView.as_view(), name='detail'), #詳細ページ
    path('<int:pk>/edit/', NoticeUpdateView.as_view(), name='edit'), #編集ページ
]   
