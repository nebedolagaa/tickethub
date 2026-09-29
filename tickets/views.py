from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, Ticket, TicketType

# maks antall billetter av én type per kjøp (samme som max på input-feltet)
MAX_TICKETS_PER_TYPE = 10


class CartError(Exception):
    pass


@login_required
def confirm_payment(request):
    if request.method != "POST":
        return redirect("tickets:payment")
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("tickets:payment")
    try:
        event_ids = {item.get("event_id") for item in cart.values()}
        if len(event_ids) != 1:
            raise CartError("Handlekurven kan bare inneholde billetter til ett arrangement.")

        # atomic + select_for_update: to kjøp samtidig kan ikke selge samme plasser
        with transaction.atomic():
            ticket_types = {
                tt.id: tt
                for tt in TicketType.objects.select_for_update()
                .select_related("event")
                .filter(pk__in=[item["ticket_type_id"] for item in cart.values()])
            }
            order = None
            for item in cart.values():
                ticket_type = ticket_types.get(item["ticket_type_id"])
                if ticket_type is None:
                    raise CartError("En av billettypene finnes ikke lenger.")
                if ticket_type.event.is_archived or ticket_type.event.end_datetime < timezone.now():
                    raise CartError("Arrangementet er avsluttet.")
                quantity = item["quantity"]
                seats_left = ticket_type.quantity - ticket_type.tickets.count()
                if quantity > seats_left:
                    raise CartError(f"Det er bare {seats_left} billetter igjen av typen {ticket_type.get_name_display()}.")

                if order is None:
                    order = Order.objects.create(user=request.user, event=ticket_type.event)
                # prisen hentes alltid fra databasen, aldri fra nettleseren
                OrderItem.objects.create(
                    order=order,
                    ticket_type=ticket_type,
                    quantity=quantity,
                    unit_price=ticket_type.price,
                )
                Ticket.objects.bulk_create(
                    [Ticket(user=request.user, ticket_type=ticket_type) for _ in range(quantity)]
                )
        del request.session["cart"]
    except CartError as e:
        messages.error(request, str(e))
        return redirect("tickets:payment")
    except (KeyError, TypeError, ValueError):
        request.session["cart"] = {}
        messages.error(request, "Noe gikk galt med handlekurven. Prøv igjen.")
        return redirect("tickets:payment")
    return redirect("tickets:after_payment")


@login_required
def payment(request):
    # Hvis POST: motta handlekurvdata og lagre i session
    if request.method == "POST" and "cart" in request.POST:
        try:
            cart_data = json.loads(request.POST["cart"])

            resolved_cart = {}
            for key, item in cart_data.items():
                ticket_type_id = item.get("ticket_type_id")
                if not ticket_type_id:
                    continue

                ticket_type = TicketType.objects.filter(pk=ticket_type_id).first()
                if not ticket_type:
                    continue

                # bare antallet kommer fra nettleseren, og det må være et gyldig tall
                quantity = int(item.get("quantity", 0))
                if not 1 <= quantity <= MAX_TICKETS_PER_TYPE:
                    continue

                # navn og pris hentes fra databasen slik at de ikke kan endres i nettleseren
                resolved_cart[str(ticket_type.id)] = {
                    "ticket_type_id": ticket_type.id,
                    "event_id": ticket_type.event_id,
                    "name": ticket_type.get_name_display(),
                    "quantity": quantity,
                    "price": float(ticket_type.price),
                }

            request.session["cart"] = resolved_cart
        except Exception:
            request.session["cart"] = {}
        return redirect("/tickets/payment/")

    # Hent cart fra session for visning
    cart = request.session.get("cart", {})
    # Heregn totaler og legg til totalpris per billettype
    cart_with_totals = {}
    total = 0
    for key, item in cart.items():
        item_total = item["quantity"] * item["price"]
        total += item_total
        cart_with_totals[key] = {**item, "item_total": item_total}
    service_fee = 70 if total else 0
    grand_total = total + service_fee
    context = {
        "cart": cart_with_totals,
        "total": total,
        "service_fee": service_fee,
        "grand_total": grand_total,
    }
    return render(request, "tickets/payment.html", context)


@login_required
def after_payment(request):
    # hent den nyeste ordren til brukeren
    order = Order.objects.filter(user=request.user).order_by("-created_at").first()

    total_amount = 0
    if order:
        # Finn summen av alle ordrelinjene
        for item in order.items.all():
            total_amount += item.quantity * item.unit_price

    context = {
        "order": order,
        "total_amount": total_amount,
    }
    return render(request, "tickets/after_payment.html", context)


def user_profile_view(request):
    return render(request, "tickets/user_profile.html")


def organizer_profile_view(request):
    return render(request, "tickets/organizer_profile.html")
