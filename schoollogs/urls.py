from django.urls import path
from .views import SchoolGrowthLogCreateView

app_name = 'schoollogs'

urlpatterns = [
    path('school_logs/new/',
        SchoolGrowthLogCreateView.as_view(),
        name='school_growthlog_create'),
]