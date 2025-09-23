# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.base_demo, name='base_demo'),  # Главная страница с демонстрацией всех компонентов
    path('demo/profile/', views.profile_demo, name='profile_demo'),
    path('', views.home, name='home'),
    path('main/', views.main, name='main'),
    path('events/', views.events, name='events'),
    path('categories/', views.categories, name='categories'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
]