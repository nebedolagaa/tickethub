from django.shortcuts import render

# Create your views here.

def my_tickets(request):
    return render(request, "tickets/my_tickets.html")

from django.shortcuts import render, redirect
import json

def betaling(request):
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
        return redirect("/billetter/betaling/")

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
    return render(request, "tickets/betaling.html", context)


def after_payment(request):
    return render(request, "tickets/after_payment.html")

def user_profile_view(request):
    return render(request, 'tickets/user_profile.html')

def organizer_profile_view(request):
    return render(request, 'tickets/organizer_profile.html')

def legg_i_handlekurv(request):
    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")
        quantity = int(request.POST.get("quantity", 1))
        price = float(request.POST.get("price"))
        name = request.POST.get("name", f"Billett {ticket_id}")

        # Hent eksisterende cart fra session
        cart = request.session.get("cart", {})

        # Oppdater cart
        if ticket_id in cart:
            cart[ticket_id]["quantity"] += quantity
        else:
            cart[ticket_id] = {
                "name": name,
                "quantity": quantity,
                "price": price
            }

        # Lagre tilbake i session
        request.session["cart"] = cart

        # Redirect til betalingsside
        return redirect("/billetter/betaling/")

    # Hvis GET, redirect tilbake til billettsiden
    return redirect("/events/purchase_tickets/")
