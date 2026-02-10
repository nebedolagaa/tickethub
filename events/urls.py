# events/urls.py
from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.home_page, name='home_page'),
    path('alle-konserter/', views.all_events, name='all_events'),
    path('festivaler/', views.festivals, name='festivals'),
    path('byer/', views.cities, name='cities'),
    path('kjop-billetter/<int:event_id>/', views.purchase_tickets, name='purchase_tickets'),
    path('snippets/', views.snippets, name='snippets'),
    path('demo/profile/', views.profile_demo, name='profile_demo'),
]