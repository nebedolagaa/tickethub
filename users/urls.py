from django.urls import path
from django.contrib.auth.views import LoginView
from .views import register, login

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name = 'register')
]