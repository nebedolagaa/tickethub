from django.shortcuts import render

# Create your views here.

def my_tickets(request):
    return render(request, "tickets/my_tickets.html")

from django.shortcuts import render, redirect
import json

def payment(request):
    # Hvis POST: motta handlekurvdata og lagre i session
    if request.method == "POST" and "cart" in request.POST:
        import json
        try:
            cart_data = json.loads(request.POST["cart"])
            request.session["cart"] = cart_data
        except Exception:
            request.session["cart"] = {}
        # Redirect til GET for å unngå repost
        from django.shortcuts import redirect
        return redirect("/tickets/payment/")

    # Hent cart fra session for visning
    cart = request.session.get("cart", {})
    # Beregn totaler og legg til totalpris per billettype
    cart_with_totals = {}
    total = 0
    for key, item in cart.items():
        item_total = item["quantity"] * item["price"]
        total += item_total
        cart_with_totals[key] = {
            **item,
            "item_total": item_total
        }
    service_fee = 70 if total else 0
    grand_total = total + service_fee
    context = {
        "cart": cart_with_totals,
        "total": total,
        "service_fee": service_fee,
        "grand_total": grand_total,
    }
    return render(request, "tickets/payment.html", context)


def after_payment(request):
    return render(request, "tickets/after_payment.html")

def user_profile_view(request):
    return render(request, 'tickets/user_profile.html')

def organizer_profile_view(request):
    return render(request, 'tickets/organizer_profile.html')


