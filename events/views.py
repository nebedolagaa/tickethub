from django.shortcuts import render
from django.http import HttpResponse
from .models import Event
from django.db.models import Q, Min

def home_page(request):
    return render(request, "home_page.html")

def all_events(request):
    """Страница со всеми концертами с возможностью поиска и сортировки"""
    events = Event.objects.all().select_related('venue', 'venue__address', 'organizer')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(venue__name__icontains=search_query) |
            Q(venue__address__city__icontains=search_query)
        )
    
    # Сортировка
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
    
    context = {
        'events': events,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_events': events.count()
    }
    
    return render(request, 'events/all_events.html', context)

def snippets(request):
    return render(request, "home_page.html")

def base_demo(request):
    """Демонстрация базового шаблона со всеми компонентами"""
    # Пример данных для демонстрации
    demo_data = {
        'tickets': [
            {
                'title': 'Aurora',
                'subtitle': 'World Tour 2024',
                'date': '15. oktober 2024',
                'time': '20:00',
                'venue': 'Oslo Spektrum, Oslo',
                'type': 'Standard',
                'seat': 'Seksjon A, Rad 15, Sete 12',
                'number': 'TH-2024-AUR-001234',
                'status': 'active',
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
                'status': 'used',
            }
        ],
        'events': [
            {
                'title': 'Aurora - World Tour 2024',
                'date': '15. oktober 2024',
                'venue': 'Oslo Spektrum',
                'price': '899 kr',
                'image_url': 'https://via.placeholder.com/300x200',
                'category': 'Musikk',
                'sold_out': False
            },
            {
                'title': 'Kvelertak Rock Festival',
                'date': '8. oktober 2024',
                'venue': 'Sentrum Scene',
                'price': 'Utsolgt',
                'image_url': 'https://via.placeholder.com/300x200',
                'category': 'Rock',
                'sold_out': True
            }
        ]
    }
    return render(request, 'home_page.html', demo_data)

def profile_demo(request):
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