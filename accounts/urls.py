from django.urls import path
#from django.contrib.auth.views import LogoutView as DjangoLogoutView
from .views import EmailLoginView

app_name = 'accounts'

urlpatterns = [
    path('login/', EmailLoginView.as_view(), name='login'),
    #path('logout/', DjangoLogoutView.as_view(), name='logout'),

]
