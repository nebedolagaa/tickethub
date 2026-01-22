from django.contrib import admin
from .models import Address, Venue, VenueArea

# Register your models here.

admin.site.register(Address)
admin.site.register(Venue)
admin.site.register(VenueArea)