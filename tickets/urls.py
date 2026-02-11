from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path("mine/", views.my_tickets, name="my_tickets"),
    path("betaling/", views.betaling, name="betaling"),
    path("after-payment/", views.after_payment, name="after_payment"),
    path('user_profile/', views.user_profile_view, name='user_profile'),
    path('organizer_profile/', views.organizer_profile_view, name='organizer_profile'),
]