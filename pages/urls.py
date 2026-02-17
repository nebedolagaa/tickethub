from django.urls import path
from . import views

urlpatterns = [
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
    path('refund/', views.refund_view, name='refund'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    path('organizer/', views.organizer_view, name='organizer'),
    path('popular-artists/', views.populaere_artister_view, name='populaere_artister'),
]
