from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, "events/home.html")

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
    return render(request, 'base_demo.html', demo_data)

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