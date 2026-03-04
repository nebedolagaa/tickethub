from django.contrib import admin
from .models import (
    Address,
    Venue,
    VenueArea,
    Event,
    EventImage,
    Row,
    Seat,
    EventSeat,
    City,
    Performer,
)

# Register your models here.

class PerformerAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_type", "venue", "start_datetime", "organizer"]
    list_filter = ["event_type", "venue__address__city", "start_datetime"]
    search_fields = ["title", "description", "performers"]
    ordering = ["start_datetime"]
    autocomplete_fields = ["performers"]


class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "image_url"]
    search_fields = ["name"]
    ordering = ["name"]


admin.site.register(Address)
admin.site.register(City, CityAdmin)
admin.site.register(Venue)
admin.site.register(VenueArea)
admin.site.register(Event, EventAdmin)
admin.site.register(EventImage)
admin.site.register(Row)
admin.site.register(Seat)
admin.site.register(EventSeat)

admin.site.register(Performer, PerformerAdmin)
@admin.register(Performer) #JF - Performer admin
class PerformerAdmin(admin.ModelAdmin):
    prepopulated_fields={"slug":("name",)}
    search_fields=("name")
    list_display = ("name","created_at")
