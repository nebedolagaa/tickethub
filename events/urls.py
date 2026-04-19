# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home_page"),
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
    # path('demo/profile/', views.profile_demo, name='profile_demo'),  # Commented out - function not implemented
    path("venue_guide/", views.venue_guide, name="venue_guide"),

    # API endpoints
    path("api/events/", views.EventListAPIView.as_view(), name="event-list-api"),
    path("api/event/<int:id>/delete/", views.EventDeleteAPIView.as_view(), name="event_delete_api"),
    path("api/events/<int:pk>/", views.EventUpdateView.as_view(), name="event-update-api"),
    path("api/cities/", views.CityListAPIView.as_view(), name="city-list-api"),
    path("api/concerts/", views.ConcertListAPIView.as_view(), name="concert-list-api"),
]
