from django.shortcuts import render

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
