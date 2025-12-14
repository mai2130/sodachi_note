from django.urls import path
from .views import BoardListView, BoardCreateView ,board_detail

app_name ="boards"

urlpatterns = [
    path("",BoardListView.as_view(),name="list"),
    path("create/", BoardCreateView.as_view(), name="create"),
    path("<int:pk>/", board_detail, name="detail"),
]

