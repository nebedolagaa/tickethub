from django.urls import path
from django.contrib.auth.views import LoginView

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
]
from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = []
