from django.urls import path
from .views import SchoolGrowthLogCreateView

app_name = 'schoollogs'

urlpatterns = [
    path('new/',
        SchoolGrowthLogCreateView.as_view(),
        name='school_growthlog_form'),
]