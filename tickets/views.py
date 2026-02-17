from django.shortcuts import render

# Create your views here.

def my_tickets(request):
    return render(request, "tickets/my_tickets.html")

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
    # Beregn totaler
    total = sum(item["quantity"] * item["price"] for item in cart.values()) if cart else 0
    service_fee = 70 if total else 0
    grand_total = total + service_fee
    context = {
        "cart": cart,
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
