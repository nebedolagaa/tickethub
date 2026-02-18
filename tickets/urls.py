from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path("my-tickets/", views.my_tickets, name="my_tickets"),
    path("payment/", views.payment, name="payment"),
    path("after-payment/", views.after_payment, name="after_payment"),

]