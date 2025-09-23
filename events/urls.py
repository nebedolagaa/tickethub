# events/urls.py
from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.home_page, name='home_page'),
    path('demo/', views.base_demo, name='base_demo'),  # Use 'demo/' for base_demo
    path('demo/profile/', views.profile_demo, name='profile_demo'),
]