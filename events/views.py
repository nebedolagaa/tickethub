from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from users.models import OrganizerProfile
from tickets.models import Ticket

from .models import Event
from .models import (
    Performer,
)  # JF- importere Artist/Performer-modellen for å kunne bruke den i views
from django.shortcuts import redirect
from django.utils.text import slugify
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
)  # JF - til performermodellen, linke opp performer med arrangement
from django.db.models import Q, Count, Min
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# REST Framework imports
from rest_framework import generics
from .serializers import EventSerializer, CitySerializer
from .models import City

# API-view for å hente ut alle byer
from rest_framework import generics

class CityListAPIView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


def home_page(request):
    """Hovedside med 3 fremhevede arrangementer (2 konserter + 1 festival)"""
    # Henter 2 konserter som ikke har gått ut og ikke er arkivert
    concerts = (
        Event.objects.filter(
            event_type="concert", end_datetime__gte=timezone.now(), is_archived=False
        )
        .select_related("venue", "venue__address", "organizer")
        .prefetch_related("images", "ticket_types")
        .order_by("start_datetime")[:2]
    )

    # Henter 1 festival som ikke har gått ut og ikke er arkivert
    festivals = (
        Event.objects.filter(
            event_type="festival", end_datetime__gte=timezone.now(), is_archived=False
        )
        .select_related("venue", "venue__address", "organizer")
        .prefetch_related("images", "ticket_types")
        .order_by("start_datetime")[:1]
    )

    # Kombinerer og konverterer til liste
    featured_events = list(concerts) + list(festivals)

    context = {"featured_events": featured_events}
    return render(request, "home_page.html", context)


def concerts(request):
    """Side med alle konserter med søke- og sorteringsfunksjonalitet"""
    # Filtrer kun konserter (ikke festivaler) som ikke har gått ut
    events = Event.objects.filter(
        event_type="concert", end_datetime__gte=timezone.now()
    ).select_related("venue", "venue__address", "organizer")

    # Søk
    search_query = request.GET.get("search", "")
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(venue__name__icontains=search_query)
            | Q(venue__address__city__icontains=search_query)
        )

    # Sortering
    sort_by = request.GET.get("sort", "date_asc")

    if sort_by == "date_asc":
        events = events.order_by("start_datetime")
    elif sort_by == "date_desc":
        events = events.order_by("-start_datetime")
    elif sort_by == "title_asc":
        events = events.order_by("title")
    elif sort_by == "title_desc":
        events = events.order_by("-title")
    elif sort_by == "venue":
        events = events.order_by("venue__name")

    # Paginering - 12 arrangementer per side
    paginator = Paginator(events, 12)
    page = request.GET.get("page")

    try:
        events_page = paginator.page(page)
    except PageNotAnInteger:
        # Hvis side ikke er et heltall, vis første side
        events_page = paginator.page(1)
    except EmptyPage:
        # Hvis side er utenfor rekkevidde, vis siste side
        events_page = paginator.page(paginator.num_pages)

    context = {
        "events": events_page,
        "search_query": search_query,
        "sort_by": sort_by,
        "total_events": paginator.count,
    }

    return render(request, "events/concerts.html", context)


def snippets(request):
    return render(request, "home_page.html")


def festivals(request):
    """Side som viser alle festivaler"""
    # Filtrer kun festivaler som ikke har gått ut og ikke er arkivert
    festivals = Event.objects.filter(
        event_type="festival", end_datetime__gte=timezone.now(), is_archived=False
    ).select_related("venue", "venue__address", "organizer")

    # Søk
    search_query = request.GET.get("search", "")
    if search_query:
        festivals = festivals.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(venue__name__icontains=search_query)
            | Q(venue__address__city__icontains=search_query)
        )

    # Sortering
    sort_by = request.GET.get("sort", "date_asc")

    if sort_by == "date_asc":
        festivals = festivals.order_by("start_datetime")
    elif sort_by == "date_desc":
        festivals = festivals.order_by("-start_datetime")
    elif sort_by == "title_asc":
        festivals = festivals.order_by("title")
    elif sort_by == "title_desc":
        festivals = festivals.order_by("-title")
    elif sort_by == "venue":
        festivals = festivals.order_by("venue__name")

    # Paginering - 12 festivaler per side
    paginator = Paginator(festivals, 12)
    page = request.GET.get("page")

    try:
        festivals_page = paginator.page(page)
    except PageNotAnInteger:
        # Hvis side ikke er et heltall, vis første side
        festivals_page = paginator.page(1)
    except EmptyPage:
        # Hvis side er utenfor rekkevidde, vis siste side
        festivals_page = paginator.page(paginator.num_pages)

    context = {
        "festivals": festivals_page,
        "search_query": search_query,
        "sort_by": sort_by,
        "total_festivals": paginator.count,
    }

    return render(request, "events/festivals.html", context)


def cities(request):
    """Side som viser alle byer med arrangementer"""
    from django.db.models import Count
    from .models import City

    # Henter alle byer med antall events (kun ikke utløpte og ikke-arkiverte) og informasjon om bilder
    cities_list = (
        Event.objects.filter(end_datetime__gte=timezone.now(), is_archived=False)
        .values("venue__address__city")
        .annotate(event_count=Count("id"))
        .order_by("-event_count", "venue__address__city")
    )

    # Søk etter bynavn
    search_query = request.GET.get("search", "")
    if search_query:
        cities_list = cities_list.filter(venue__address__city__icontains=search_query)

    # Sortering
    sort_by = request.GET.get("sort", "events_desc")

    if sort_by == "events_desc":
        cities_list = cities_list.order_by("-event_count")
    elif sort_by == "events_asc":
        cities_list = cities_list.order_by("event_count")
    elif sort_by == "name_asc":
        cities_list = cities_list.order_by("venue__address__city")
    elif sort_by == "name_desc":
        cities_list = cities_list.order_by("-venue__address__city")

    # Legger til informasjon om bybilder fra City-modellen
    city_images = {city.name: city.image_url for city in City.objects.all()}

    # Beriker bydata med bilder
    cities_with_images = []
    for city in cities_list:
        city_name = city["venue__address__city"]
        city_data = {
            "venue__address__city": city_name,
            "event_count": city["event_count"],
            "image_url": city_images.get(
                city_name,
                "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=800&q=80",
            ),  # standardbilde
        }
        cities_with_images.append(city_data)

    context = {
        "cities": cities_with_images,
        "search_query": search_query,
        "sort_by": sort_by,
        "total_cities": len(cities_with_images),
    }

    return render(request, "events/cities.html", context)


def purchase_tickets(request, event_id):
    """Side for kjøp av billetter til en konsert"""
    from tickets.models import TicketType, Ticket
    from django.contrib import messages

    event = get_object_or_404(
        Event.objects.select_related("venue", "venue__address", "organizer"),
        pk=event_id,
    )

    ticket_types = TicketType.objects.filter(event=event).select_related("venue_area")

    if request.method == "POST":
        ticket_type_id = request.POST.get("ticket_type_id")
        quantity = int(request.POST.get("quantity", 1))
        ticket_type = get_object_or_404(TicketType, id=ticket_type_id, event=event)

        sold_count = ticket_type.tickets.count()
        seats_left = ticket_type.quantity - sold_count

        if quantity > seats_left:
            messages.error(request, "Ikke nok billetter igjen.")
        else:
            for _ in range(quantity):
                Ticket.objects.create(
                    user=request.user,
                    ticket_type=ticket_type,
                )
            messages.success(request, f"{quantity} billett(er) kjøpt!")
            return redirect("purchase_tickets", event_id=event_id)

    formatted_tickets = []
    for ticket_type in ticket_types:
        sold_count = ticket_type.tickets.count()
        seats_left = ticket_type.quantity - sold_count
        description = ""
        if "VIP" in ticket_type.name:
            description = "VIP-billett med ekstra fordeler og beste plassering"
        elif "Ståplass" in ticket_type.name or "Standing" in ticket_type.name:
            description = "Ståplass - generell adgang"
        elif "Student" in ticket_type.name:
            description = "Studentbillett - gyldig studentbevis kreves"
        elif "Early Bird" in ticket_type.name:
            description = "Tidligbillett - begrenset antall"
        else:
            description = f"Ordinær billett - {ticket_type.venue_area.name}"

        formatted_tickets.append(
            {
                "id": ticket_type.id,
                "name": ticket_type.name,
                "price": int(ticket_type.price),
                "description": description,
                "available": seats_left > 0,
                "seats_left": seats_left,
                "venue_area": ticket_type.venue_area.name,
            }
        )

    context = {
        "event": event,
        "ticket_types": formatted_tickets,
    }

    return render(request, "events/purchase_tickets.html", context)


def venue_guide(request):
    """Side som viser en guide til de mest populære konsertstedene i Norge"""
    from .models import Venue

    # Henter venues sortert etter hvor mange aktive events de har, viser topp 10
    venues = (
        Venue.objects.annotate(
            event_count=Count(
                "events",
                filter=Q(
                    events__end_datetime__gte=timezone.now(), events__is_archived=False
                ),
            )
        )
        .order_by("-event_count")[:10]
        .select_related("address")
    )

    context = {"venues": venues}
    return render(request, "events/venue_guide.html", context)


def venues(request):
    """Side som viser alle venues med søke- og sorteringsfunksjonalitet"""
    from .models import Venue

    # Henter alle venues
    venues_list = Venue.objects.select_related("address").all()

    # Søk
    search_query = request.GET.get("search", "")
    if search_query:
        venues_list = venues_list.filter(
            Q(name__icontains=search_query)
            | Q(address__city__icontains=search_query)
            | Q(address__street__icontains=search_query)
        )

    # Sortering
    sort_by = request.GET.get("sort", "title_asc")

    if sort_by == "title_asc":
        venues_list = venues_list.order_by("name")
    elif sort_by == "title_desc":
        venues_list = venues_list.order_by("-name")
    elif sort_by == "venue":
        venues_list = venues_list.order_by("address__city")

    # Paginering - 12 venues per side
    paginator = Paginator(venues_list, 12)
    page = request.GET.get("page")

    try:
        venues_page = paginator.page(page)
    except PageNotAnInteger:
        # Hvis side ikke er et heltall, vis første side
        venues_page = paginator.page(1)
    except EmptyPage:
        # Hvis side er utenfor rekkevidde, vis siste side
        venues_page = paginator.page(paginator.num_pages)

    context = {
        "venues": venues_page,
        "search_query": search_query,
        "sort_by": sort_by,
        "total_venues": paginator.count,
    }

    return render(request, "events/venue_guide.html", context)


def venue_detail(request, venue_id):
    """Side som viser detaljer om en spesifikk venue"""
    from .models import Venue

    venue = get_object_or_404(Venue.objects.select_related("address"), pk=venue_id)

    # Henter events som finner sted på denne venueen (kun ikke utløpte og ikke-arkiverte)
    events = (
        Event.objects.filter(
            venue=venue, end_datetime__gte=timezone.now(), is_archived=False
        )
        .select_related("organizer", "venue", "venue__address")
        .prefetch_related("images", "ticket_types")
    )

    context = {
        "venue": venue,
        "events": events,
    }

    return render(request, "events/venue_detail.html", context)


# REST API Views
#MB og JF:
class EventUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    partial = True


class PerformerListView(ListView):  #JF - View for å vise alle artister
    model = Performer
    template_name = "performer/performer_list.html"
    context_object_name = "performers"
    paginate_by = 10


class PerformerDetailView(
    DetailView
):  # JF - View for å vise detaljer om en spesifikk artist
    model = Performer
    template_name = "events/performer_detail.html"
    slug_field = "slug"
    context_object_name = "performer"


#api for å fjerne en event fra listen over sine arrangementer på arrangør siden
class EventDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        return Response({"message": "Bruk DELETE-metoden for å slette arrangementet."})

    def delete(self, request, id):
        try:
            organizer = OrganizerProfile.objects.get(user=request.user)
        except OrganizerProfile.DoesNotExist:
            return Response(
                {"message": "Du har ikke tilgang som arrangør."},
                status=status.HTTP_403_FORBIDDEN)
        
        try:
            event = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Arrangementet finnes ikke."},
                status=status.HTTP_404_NOT_FOUND
            )

        if event.organizer != organizer:
            return Response(
                {"error": "Du har ikke tilgang til å slette dette arrangementet."},
                status=status.HTTP_403_FORBIDDEN
            )

        if Ticket.objects.filter(ticket_type__event = event).exists():
            return Response({"message": "Arrangement kan ikke slettes fordi det har tilknyttede biletter."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        event.delete()
        return Response({"message": "Arrangementet ble slettet."},
                        status=status.HTTP_204_NO_CONTENT)