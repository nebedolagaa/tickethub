from django.contrib import admin
from .models import Address, Venue, VenueArea, Event, EventImage, Row, Seat, EventSeat

# Register your models here.

admin.site.register(Address)
admin.site.register(Venue)
admin.site.register(VenueArea)
admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(Row)
admin.site.register(Seat)
admin.site.register(EventSeat)