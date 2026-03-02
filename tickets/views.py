from django.shortcuts import render, redirect
import json
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, Ticket, TicketType

def my_tickets(request):
    return render(request, "tickets/my_tickets.html")

@login_required
def confirm_payment(request):
    # Hent cart fra session
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("tickets:payment")

    # Finn event_id fra cart-data (forutsetter at alle varer er fra samme event)
    event_id = next(iter(cart.values()))["event_id"]
    order = Order.objects.create(user=request.user, event_id=event_id)

    for key, item in cart.items():
        ticket_type = TicketType.objects.get(pk=item["ticket_type_id"])
        order_item = OrderItem.objects.create(
            order=order,
            ticket_type=ticket_type,
            quantity=item["quantity"],
            unit_price=item["price"]
        )
        # Opprett én Ticket per billett
        for _ in range(item["quantity"]):
            Ticket.objects.create(
                user=request.user,
                ticket_type=ticket_type
            )

    # Tøm handlekurven
    del request.session["cart"]
    return redirect("tickets:after_payment")

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


