from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path("mine/", views.my_tickets, name="my_tickets"),
    path("betaling/", views.betaling, name="betaling"),
]