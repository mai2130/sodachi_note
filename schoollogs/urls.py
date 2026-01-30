from django.urls import path
from .views import SchoolGrowthLogView, HomeGrowthLogView
from . import views

app_name = 'schoollogs'

urlpatterns = [
    path('school/',
        SchoolGrowthLogView.as_view(),
        name='school_growthlog_form'),
    path('home/',
        HomeGrowthLogView.as_view(),
        name='home_growthlog_form'),
    path('select-child/',
        views.select_child,
        name='select_child'),
]