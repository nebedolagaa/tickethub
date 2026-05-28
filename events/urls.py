# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("all-events/", views.all_events, name="all_events"),
    path("concerts/", views.concerts, name="concerts"),
    path("festivals/", views.festivals, name="festivals"),
    path("venues/", views.venues, name="venues"),
    path("venues/<int:venue_id>/", views.venue_detail, name="venue_detail"),
    path("cities/", views.cities, name="cities"),
    path(
        "purchase-tickets/<int:event_id>/",
        views.purchase_tickets,
        name="purchase_tickets",
    ),
    path("snippets/", views.snippets, name="snippets"),
    # API endpoints
    path(
        "api/event/<int:id>/delete/",
        views.EventDeleteAPIView.as_view(),
        name="event_delete_api",
    ),
    path(
        "api/events/<int:pk>/", views.EventUpdateView.as_view(), name="event-update-api"
    ),
    path("api/cities/", views.CityListAPIView.as_view(), name="city-list-api"),
    path("api/events/", views.EventListAPIView.as_view(), name="event-list-api"),
    path("api/performers/search/", views.performer_search_api, name="performer-search-api"),
]
