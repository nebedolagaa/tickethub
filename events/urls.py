# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('demo/profile/', views.profile_demo, name='profile_demo'),
]