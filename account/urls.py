from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.login, name = 'account-login'),
    path('logout', views.logout, name = 'account-logout'),
    path('get-cookies', views.getCookies, name='account-coookies'),
]