from django.contrib import admin
from .models import TicketType, Ticket, Order, OrderItem, OrderSeat

admin.site.register(TicketType)
admin.site.register(Ticket)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderSeat)
