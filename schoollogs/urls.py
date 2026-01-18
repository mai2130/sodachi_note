from django.urls import path
from .views import SchoolGrowthLogView, HomeGrowthLogView

app_name = 'schoollogs'

urlpatterns = [
    path('school/',
        SchoolGrowthLogView.as_view(),
        name='school_growthlog_form'),
    path('home/',
        HomeGrowthLogView.as_view(),
        name='home_growthlog_form'),

]