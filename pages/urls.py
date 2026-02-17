from django.urls import path
from . import views

urlpatterns = [
    path('faq/', views.faq_view, name='faq'),
    path('kontakt/', views.kontakt_view, name='kontakt'),
    path('refusjon/', views.refusjon_view, name='refusjon'),
    path('personvern/', views.personvern_view, name='personvern'),
    path('vilkar/', views.vilkar_view, name='vilkar'),
    path('arrangor/', views.arrangor_view, name='arrangor'),
    path('populære_artister/', views.populaere_artister_view, name='populaere_artister' ),
]
