# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Use 'home' for root
    path('demo/', views.base_demo, name='base_demo'),  # Use 'demo/' for base_demo
    path('demo/profile/', views.profile_demo, name='profile_demo'),
    path('main/', views.main, name='main'),
    path('events/', views.events, name='events'),
    path('categories/', views.categories, name='categories'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
]