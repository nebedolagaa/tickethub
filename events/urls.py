# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("all-events/", views.all_events, name="all_events"),
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
]
