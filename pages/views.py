import os

from django.conf import settings
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from events.models import Performer

# Create your views here.

def faq_view(request):
    return render(request, 'pages/faq.html')

def contact_view(request):
    return render(request, 'pages/contact.html')

def refund_view(request):
    return render(request, 'pages/refund.html')

def privacy_view(request):
    return render(request, 'pages/privacy.html')

def terms_view(request):
    return render(request, 'pages/terms.html')

def organizer_view(request):
    return render(request, 'pages/organizer.html')

def populaere_artister_view(request):
    now = timezone.now()
    performers = (
        Performer.objects.annotate(
            event_count=Count(
                "events",
                filter=Q(events__end_datetime__gte=now, events__is_archived=False),
                distinct=True,
            )
        )
        .order_by("-event_count", "name")
    )

    fallback_images = [
        "https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?auto=format&fit=crop&w=600&q=80",
    ]

    for index, performer in enumerate(performers):
        image_exists = (
            performer.image
            and os.path.exists(os.path.join(settings.MEDIA_ROOT, performer.image.name))
        )
        performer.display_image_url = (
            performer.image.url if image_exists else fallback_images[index % len(fallback_images)]
        )
        performer.display_genre = performer.get_genre_display() or "Other"

    context = {'performers': performers}
    return render(request, 'pages/popular_artists.html', context)
