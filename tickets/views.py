from django.shortcuts import render

# Create your views here.

def my_tickets(request):
    return render(request, "tickets/my_tickets.html")

def betaling(request):
    return render(request, "tickets/betaling.html")