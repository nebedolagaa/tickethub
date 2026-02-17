from django.shortcuts import render

# Create your views here.

def faq_view(request):
    return render(request, 'pages/faq.html')

def kontakt_view(request):
    return render(request, 'pages/kontakt.html')

def refusjon_view(request):
    return render(request, 'pages/refusjon.html')

def personvern_view(request):
    return render(request, 'pages/personvern.html')

def vilkar_view(request):
    return render(request, 'pages/vilkar.html')

def arrangor_view(request):
    return render(request, 'pages/arrangor.html')

def populaere_artister_view(request):
    return render(request, 'pages/popular_artists.html')
