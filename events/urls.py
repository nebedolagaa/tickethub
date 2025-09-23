# events/urls.py
from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.home_page, name='home_page'),
    path('snippets/', views.snippets, name='snippets'),
    path('demo/profile/', views.profile_demo, name='profile_demo'),
]