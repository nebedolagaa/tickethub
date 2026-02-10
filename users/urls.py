from django.urls import path
from django.contrib.auth.views import LoginView
from .views import register, login, forgotPassword, resetpassword_validate, resetPassword

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name = 'register'),

    path('forgotPassword/',  forgotPassword, name = 'forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', resetpassword_validate, name = 'resetpassword_validate'),
    path('resetPassword/', resetPassword, name = 'resetPassword'),
]