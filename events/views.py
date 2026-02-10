from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Event
from django.db.models import Q, Min
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home_page(request):
    """Hovedside med 3 fremhevede arrangementer (2 konserter + 1 festival)"""
    # Henter 2 konserter
    concerts = Event.objects.filter(
        event_type='concert'
    ).select_related(
        'venue', 'venue__address', 'organizer'
    ).prefetch_related(
        'images', 'ticket_types'
    ).order_by('start_datetime')[:2]
    
    # Henter 1 festival
    festivals = Event.objects.filter(
        event_type='festival'
    ).select_related(
        'venue', 'venue__address', 'organizer'
    ).prefetch_related(
        'images', 'ticket_types'
    ).order_by('start_datetime')[:1]
    
    # Kombinerer og konverterer til liste
    featured_events = list(concerts) + list(festivals)
    
    context = {
        'featured_events': featured_events
    }
    return render(request, "home_page.html", context)

def all_events(request):
    """Side med alle konserter med søke- og sorteringsfunksjonalitet"""
    # Filtrer kun konserter (ikke festivaler)
    events = Event.objects.filter(event_type='concert').select_related('venue', 'venue__address', 'organizer')
    
    # Søk
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(venue__name__icontains=search_query) |
            Q(venue__address__city__icontains=search_query)
        )
    
    # Sortering
    sort_by = request.GET.get('sort', 'date_asc')
    
    if sort_by == 'date_asc':
        events = events.order_by('start_datetime')
    elif sort_by == 'date_desc':
        events = events.order_by('-start_datetime')
    elif sort_by == 'title_asc':
        events = events.order_by('title')
    elif sort_by == 'title_desc':
        events = events.order_by('-title')
    elif sort_by == 'venue':
        events = events.order_by('venue__name')
    
    # Paginering - 12 arrangementer per side
    paginator = Paginator(events, 12)
    page = request.GET.get('page')
    
    try:
        events_page = paginator.page(page)
    except PageNotAnInteger:
        # Hvis side ikke er et heltall, vis første side
        events_page = paginator.page(1)
    except EmptyPage:
        # Hvis side er utenfor rekkevidde, vis siste side
        events_page = paginator.page(paginator.num_pages)
    
    context = {
        'events': events_page,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_events': paginator.count
    }
    
    return render(request, 'events/all_events.html', context)

def snippets(request):
    return render(request, "home_page.html")

def festivals(request):
    """Side som viser alle festivaler"""
    # Filtrer kun festivaler
    festivals = Event.objects.filter(event_type='festival').select_related('venue', 'venue__address', 'organizer')
    
    # Søk
    search_query = request.GET.get('search', '')
    if search_query:
        festivals = festivals.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(venue__name__icontains=search_query) |
            Q(venue__address__city__icontains=search_query)
        )
    
    # Sortering
    sort_by = request.GET.get('sort', 'date_asc')
    
    if sort_by == 'date_asc':
        festivals = festivals.order_by('start_datetime')
    elif sort_by == 'date_desc':
        festivals = festivals.order_by('-start_datetime')
    elif sort_by == 'title_asc':
        festivals = festivals.order_by('title')
    elif sort_by == 'title_desc':
        festivals = festivals.order_by('-title')
    elif sort_by == 'venue':
        festivals = festivals.order_by('venue__name')
    
    # Paginering - 12 festivaler per side
    paginator = Paginator(festivals, 12)
    page = request.GET.get('page')
    
    try:
        festivals_page = paginator.page(page)
    except PageNotAnInteger:
        # Hvis side ikke er et heltall, vis første side
        festivals_page = paginator.page(1)
    except EmptyPage:
        # Hvis side er utenfor rekkevidde, vis siste side
        festivals_page = paginator.page(paginator.num_pages)
    
    context = {
        'festivals': festivals_page,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_festivals': paginator.count
    }
    
    return render(request, 'events/festivals.html', context)

def cities(request):
    """Side som viser alle byer med arrangementer"""
    from django.db.models import Count
    
    # Henter alle byer med antall events
    cities_list = (
        Event.objects
        .values('venue__address__city')
        .annotate(event_count=Count('id'))
        .order_by('-event_count', 'venue__address__city')
    )
    
    # Søk etter bynavn
    search_query = request.GET.get('search', '')
    if search_query:
        cities_list = cities_list.filter(venue__address__city__icontains=search_query)
    
    # Sortering
    sort_by = request.GET.get('sort', 'events_desc')
    
    if sort_by == 'events_desc':
        cities_list = cities_list.order_by('-event_count')
    elif sort_by == 'events_asc':
        cities_list = cities_list.order_by('event_count')
    elif sort_by == 'name_asc':
        cities_list = cities_list.order_by('venue__address__city')
    elif sort_by == 'name_desc':
        cities_list = cities_list.order_by('-venue__address__city')
    
    context = {
        'cities': cities_list,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_cities': cities_list.count()
    }
    
    return render(request, 'events/cities.html', context)

def purchase_tickets(request, event_id):
    """Side for kjøp av billetter til en konsert"""
    from tickets.models import TicketType
    
    # Henter arrangementet eller returnerer 404 hvis det ikke finnes
    event = get_object_or_404(
        Event.objects.select_related('venue', 'venue__address', 'organizer'),
        pk=event_id
    )
    
    # Henter billetttyper fra databasen
    ticket_types = TicketType.objects.filter(event=event).select_related('venue_area')
    
    # Formater billetttyper for template
    formatted_tickets = []
    for ticket_type in ticket_types:
        # Beregn antall solgte billetter
        sold_count = ticket_type.tickets.count()
        seats_left = ticket_type.quantity - sold_count
        
        # Beskrivelse basert på navn
        description = ''
        if 'VIP' in ticket_type.name:
            description = 'VIP-billett med ekstra fordeler og beste plassering'
        elif 'Ståplass' in ticket_type.name or 'Standing' in ticket_type.name:
            description = 'Ståplass - generell adgang'
        elif 'Student' in ticket_type.name:
            description = 'Studentbillett - gyldig studentbevis kreves'
        elif 'Early Bird' in ticket_type.name:
            description = 'Tidligbillett - begrenset antall'
        else:
            description = f'Ordinær billett - {ticket_type.venue_area.name}'
        
        formatted_tickets.append({
            'id': ticket_type.id,
            'name': ticket_type.name,
            'price': int(ticket_type.price),
            'description': description,
            'available': seats_left > 0,
            'seats_left': seats_left,
            'venue_area': ticket_type.venue_area.name
        })
    
    context = {
        'event': event,
        'ticket_types': formatted_tickets,
    }
    
    return render(request, 'events/purchase_tickets.html', context)

def profile_demo(request):
    """Demo view for profil side - kun for testing/demonstrasjon"""
    tickets = [
        {
            'title': 'Aurora',
            'subtitle': 'World Tour 2024',
            'date': '15. oktober 2024',
            'time': '20:00',
            'venue': 'Oslo Spektrum, Oslo',
            'type': 'Standard',
            'seat': 'Seksjon A, Rad 15, Sete 12',
            'number': 'TH-2024-AUR-001234',
            'status': 'active',      # <-- Aktiv
        },
        {
            'title': 'Nils Petter Molvær',
            'subtitle': 'Summer Jazz Night',
            'date': '12. september 2024',
            'time': '19:30',
            'venue': 'Blå, Oslo',
            'type': 'VIP',
            'seat': 'Bord 5',
            'number': 'TH-2024-NPM-005678',
            'status': 'used',        # <-- Brukt
        },
        {
            'title': 'Kvelertak',
            'subtitle': 'Rock Festival',
            'date': '8. oktober 2024',
            'time': '21:00',
            'venue': 'Sentrum Scene, Oslo',
            'type': 'Early Bird',
            'seat': 'Ståplass',
            'number': 'TH-2024-KVE-009012',
            'status': 'cancelled',   # <-- Kansellert
        },
    ]
    return render(request, 'events/profile_demo.html', {'tickets': tickets})