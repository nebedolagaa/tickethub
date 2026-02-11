from django.shortcuts import render

# Create your views here.

def my_tickets(request):
    return render(request, "tickets/my_tickets.html")

def betaling(request):
    return render(request, "tickets/betaling.html")

def after_payment(request):
    return render(request, "tickets/after_payment.html")

def user_profile_view(request):
    return render(request, 'tickets/user_profile.html')

def organizer_profile_view(request):
    return render(request, 'tickets/organizer_profile.html')
