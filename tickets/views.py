from django.shortcuts import render

# Create your views here.

def my_tickets(request):
    return render(request, "tickets/my_tickets.html")

from django.shortcuts import render, redirect
import json

def betaling(request):
    # Hvis POST inneholder cart, oppdater session
    if request.method == "POST" and "cart" in request.POST:
        try:
            cart_data = json.loads(request.POST["cart"])
            request.session["cart"] = cart_data
        except Exception:
            request.session["cart"] = {}
        return redirect("/billetter/betaling/")  # redirect for å unngå repost

    # Hent cart fra session for visning (trygg default tom dict)
    cart = request.session.get("cart", {})

    # Beregn totaler og total per billettype
    cart_with_totals = {}
    total = 0
    for key, item in cart.items():
        try:
            quantity = int(item.get("quantity", 0))
            price = float(item.get("price", 0))
            item_total = quantity * price
        except Exception:
            quantity = 0
            price = 0
            item_total = 0
        total += item_total
        cart_with_totals[key] = {
            **item,
            "item_total": item_total
        }

    # Service fee hvis total > 0
    service_fee = 70 if total > 0 else 0
    grand_total = total + service_fee

    context = {
        "cart": cart_with_totals,
        "total": total,
        "service_fee": service_fee,
        "grand_total": grand_total,
    }

    return render(request, "tickets/betaling.html", context)


def after_payment(request):
    return render(request, "tickets/after_payment.html")

def user_profile_view(request):
    return render(request, 'tickets/user_profile.html')

def organizer_profile_view(request):
    return render(request, 'tickets/organizer_profile.html')
