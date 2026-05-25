from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path("payment/", views.payment, name="payment"),
    path("after-payment/", views.after_payment, name="after_payment"),
    path("confirm-payment/", views.confirm_payment, name="confirm_payment"),
]
