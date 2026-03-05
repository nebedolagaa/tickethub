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
    ArchivedEvent,
    ArchivedEventImage,
)

# Register your models here.


class EventAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "event_type",
        "venue",
        "start_datetime",
        "organizer",
        "is_archived",
    ]
    list_filter = [
        "event_type",
        "venue__address__city",
        "start_datetime",
        "is_archived",
    ]
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


@admin.register(Performer)
class PerformerAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_display = ("name",)


@admin.register(ArchivedEvent)
class ArchivedEventAdmin(admin.ModelAdmin):
    # Admin-panel for arkiverte arrangementer
    # Bidrag til denne filen: Nikita Pushechnikov
    list_display = [
        "title",
        "event_type",
        "venue_name",
        "start_datetime",
        "archived_at",
        "total_tickets_sold",
        "total_revenue",
    ]
    list_filter = ["event_type", "archived_at", "start_datetime"]
    search_fields = ["title", "description", "venue_name", "performers_list"]
    ordering = ["-archived_at"]
    readonly_fields = [
        "original_event_id",
        "organizer_name",
        "venue_name",
        "venue_address",
        "title",
        "description",
        "performers_list",
        "event_type",
        "start_datetime",
        "end_datetime",
        "created_at",
        "archived_at",
        "slug",
        "total_tickets_sold",
        "total_revenue",
    ]

    def has_add_permission(self, request):
        # Forbyd manuell opprettelse av arkivoppføringer
        return False

    def has_delete_permission(self, request, obj=None):
        # Tillat bare superadmin å slette
        return request.user.is_superuser


@admin.register(ArchivedEventImage)
class ArchivedEventImageAdmin(admin.ModelAdmin):
    # Admin-panel for arkiverte arrangementsbilder
    # Bidrag til denne filen: Nikita Pushechnikov
    list_display = ["archived_event", "image_path", "is_cover"]
    list_filter = ["is_cover"]
    search_fields = ["archived_event__title", "alt_text"]
    readonly_fields = ["archived_event", "image_path", "alt_text", "is_cover"]

    def has_add_permission(self, request):
        return False
