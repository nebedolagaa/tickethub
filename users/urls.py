from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login-test/", views.login_test, name="login_test"),
]

