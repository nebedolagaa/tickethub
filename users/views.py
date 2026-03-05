"""
Bidratt til denne filen:
    - Kamilla Nizamova
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages, auth
from django.db.models import Sum, F

from django.contrib.auth.decorators import login_required

from .models import Account, UserProfile, OrganizerProfile
from tickets.models import Ticket, Order
from events.models import Event

from django.db.models import F, Sum, DecimalField, Value
from django.db.models.functions import Coalesce, Cast

from .forms import (
    AccountCreationForm,
    SignupTypeForm,
    OrganizerProfileForm,
    UserForm,
    UserProfileForm,
)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Min

# verifikasjonsverktøy for tilbakestilling av passord
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils import timezone
import base64
import io

try:
    import qrcode
except ImportError:
    qrcode = None


# funksjon for registrering av bruker
def register(request):
    if request.method == "POST":
        user_form = AccountCreationForm(request.POST)
        type_form = SignupTypeForm(request.POST)

        type_valid = (
            type_form.is_valid()
        )  # sjekk om type_form er gyldig før du prøver å hente data fra den
        is_organizer = type_valid and type_form.cleaned_data.get(
            "is_organizer", False
        )  # henter boolean fra checkbox (False hvis ikke huket av)

        organizer_form = (
            OrganizerProfileForm(request.POST)
            if is_organizer
            else OrganizerProfileForm()
        )  # tom form hvis ikke arrangør

        ok = (
            user_form.is_valid() and type_valid
        )  # brukerform og type_form må være gyldige for å fortsette
        if is_organizer:
            # legger inn en ny condition for ok
            ok = (
                ok and organizer_form.is_valid()
            )  # hvis arrangør må også arrangørprofilen være gyldig

        if ok:
            with transaction.atomic():  # hvis noe går galt under opprettelsen av bruker eller arrangørprofil, vil ingen av dem bli opprettet
                user = user_form.save(commit=False)
                user.email = (
                    user.email.lower()
                )  # sørg for at e-posten alltid lagres i små bokstaver
                user.save()

                UserProfile.objects.create(
                    user=user
                )  # opprett en tilhørende brukerprofil for denne brukeren, selv om det ikke er arrangør, for å lagre info som er felles for alle brukere

                if is_organizer:
                    organizer = organizer_form.save(commit=False)
                    organizer.user = user  # knytt arrangørprofilen til user fordi arrangør er en rolle og ikke en egen user type
                    organizer.save()

            auth.login(request, user)
            messages.success(request, "Konto opprettet og du er nå logget inn")
            return redirect("home_page")  # omdiriger til hjemsiden etter registrering

    else:
        user_form = AccountCreationForm()
        type_form = SignupTypeForm()
        organizer_form = OrganizerProfileForm()

    # hvis det er en GET request eller hvis det er en POST request med ugyldige data, render registreringssiden med formene
    # (som vil vise valideringsfeil hvis det var en POST request)
    return render(
        request,
        "users/register.html",
        {
            "user_form": user_form,
            "type_form": type_form,
            "organizer_form": organizer_form,
        },
    )


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("home_page")
        else:
            messages.error(request, "Ugyldig e-post eller passord")
            return redirect("users:login")

    return render(request, "users/login.html")


@login_required(login_url="users:login")
def logout(request):
    auth.logout(request)
    messages.success(request, "Du er nå logget ut")
    return redirect("home_page")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            # send email with reset link
            user = Account.objects.get(email__exact=email)

            # reset password email
            current_site = get_current_site(request)
            mail_subject = "Passord bytte forespørsel"
            message = render_to_string(
                "users/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(
                        force_bytes(user.pk)
                    ),  # encode user id for å sende i url, safe metode
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request,
                "En e-post har blitt sendt til "
                + email
                + " med instruksjoner for å tilbakestille passordet ditt.",
            )
            return redirect("users:login")
        else:
            messages.error(request, "E-postadressen finnes ikke i systemet")
            return redirect("users:forgotPassword")

    return render(request, "users/forgotPassword.html")


# funksjon for å validere token og uid fra reset password linken i e-posten, og om de er gyldige, lagre uid i session for å bruke i resetPassword view
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # dekode uid fra url
        user = Account._default_manager.get(pk=uid)  # hent bruker basert på dekodet uid
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(
        user, token
    ):  # sjekk at token er gyldig for denne brukeren
        request.session["uid"] = (
            uid  # lagre uid i session for å bruke i reset passord view
        )
        messages.success(request, "Vennligst tilbakestill passordet ditt")
        return redirect("users:resetPassword")
    else:
        messages.error(request, "Linken for tilbakestilling av passord er ugyldig")
        return redirect("users:forgotPassword")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")  # hent uid fra session
            user = Account.objects.get(pk=uid)  # hent bruker basert på uid
            user.set_password(
                password
            )  # bruk set_password for å hashe passordet før det lagres i databasen, byggt inn metode i Django's User model
            user.save()
            messages.success(
                request,
                "Passordet ditt har blitt tilbakestilt. Du kan nå logge inn med det nye passordet ditt.",
            )
            return redirect("users:login")

        else:
            messages.error(request, "Passordene matcher ikke")
            return redirect("users:resetPassword")

    else:
        return render(request, "users/resetPassword.html")


# her kommer det funkjoner for å vise og redigere brukerprofiler, både for vanlige brukere og arrangører
@login_required(login_url="users:login")
def user_profile(request):
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)
    extra_info = userprofile

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)

        profile_form = UserProfileForm(request.POST, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Din profil har blitt oppdatert")
            return redirect("users:user_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        "extra_info": extra_info,
        "user_form": user_form,
        "profile_form": profile_form,
    }

    return render(request, "users/user_profile.html", context)


@login_required(login_url="users:login")
def my_orders(request):
    def build_qr_data_uri(payload: str) -> str:
        if qrcode is None:
            return ""

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=1,
        )
        qr.add_data(payload)
        qr.make(fit=True)

        image = qr.make_image(fill_color="#ffffff", back_color="#111111")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    now = timezone.now()

    tickets = (
        Ticket.objects.filter(
            user=request.user,
            ticket_type__event__end_datetime__gte=now,
        )
        .select_related(
            "ticket_type",
            "ticket_type__event",
            "ticket_type__event__venue",
            "ticket_type__event__venue__address",
            "event_seat__seat",
        )
        .prefetch_related("ticket_type__event__performers")
        .order_by("ticket_type__event__start_datetime")
    )  # hent alle ordre for denne brukeren, sortert etter dato (nyeste først)
    tickets_count = (
        tickets.count()
    )  # hent antall ordre for denne brukeren, for å vise i profilen

    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created_at")
        .annotate(
            total_amount=Coalesce(
                Sum(
                    Cast(
                        "items__quantity", DecimalField(max_digits=10, decimal_places=2)
                    )
                    * F("items__unit_price")
                ),
                0,
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
    )
    # have to use coalesce to return 0 instead of None for orders with no items, otherwise it will cause an error and template will not load.
    # tries several expression to multiply quantity and unit_price for each order item (both are different datatypes)
    # i ended up using cast because it was the only one that worked..

    # hent alle ordre for denne brukeren, sortert etter dato (nyeste først)

    extra_info, _ = UserProfile.objects.get_or_create(user=request.user)

    totaly_used = Order.objects.filter(user=request.user).aggregate(
        total=Coalesce(
            Sum(
                Cast("items__quantity", DecimalField(max_digits=10, decimal_places=2))
                * F("items__unit_price")
            ),
            Value(0),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )["total"]

    # henter antall arrangement som kommer i fremtiden, regnes ved hjelp av unike arrangement og ikke biletter
    upcoming_events = tickets.values("ticket_type__event").distinct().count()

    for ticket in tickets:
        ticket.qr_data_uri = build_qr_data_uri(str(ticket.ticket_number))

    context = {
        "orders": orders,
        "extra_info": extra_info,
        "totaly_used": totaly_used,
        "tickets_count": tickets_count,
        "tickets": tickets,
        "upcoming_events": upcoming_events,
    }

    return render(request, "users/my_orders.html", context)


@login_required(login_url="users:login")
def organizer_profile(request):
    # Sjekk om brukeren har arrangørprofil
    try:
        organizer = OrganizerProfile.objects.get(user=request.user)
    except OrganizerProfile.DoesNotExist:
        messages.error(
            request,
            "Du har ikke tilgang til arrangørprofil. Kun brukere registrert som arrangører kan se denne siden.",
        )
        return redirect("users:user_profile")

    # dette er koden for å oppdatere arrangørprofil
    if request.method == "POST":

        # check if its a request to delete an event
        if "delete_event_id" in request.POST:
            event_id = request.POST["delete_event_id"]
            event = get_object_or_404(
                Event, id=event_id, organizer=organizer
            )  # sjekk at eventet tilhører denne arrangøren for sikkerhet

            if Ticket.objects.filter(ticket_type__event=event).exists():
                messages.error(
                    request,
                    "Arrangementet kan ikke slettes fordi det finnes billetter.",
                    extra_tags="event",
                )
                return redirect("users:organizer_profile")
            else:
                event.delete()

                messages.success(
                    request, "Arrangementet ble slettet", extra_tags="event"
                )
                return redirect("users:organizer_profile")

        organizer_form = OrganizerProfileForm(request.POST, instance=organizer)

        if organizer_form.is_valid():
            organizer_form.save()

            messages.success(
                request, "Din profil har blitt oppdatert", extra_tags="profile"
            )
            return redirect("users:organizer_profile")
    else:
        organizer_form = OrganizerProfileForm(instance=organizer)


    # koden for statistikk
    events = Event.objects.filter(organizer=request.user.organizer_profile).order_by(
        "start_datetime"
    )
    total_events = events.count()
    active_events = events.filter(start_datetime__gte=timezone.now()).count()

    # Beregn antall solgte billetter for organisatorens arrangementer
    # Forfatter: Nikita Pushechnikov
    sold_tickets = Ticket.objects.filter(
        ticket_type__event__organizer=request.user.organizer_profile
    ).count()

    # Beregn total omsetning for organisatorens arrangementer
    # Forfatter: Nikita Pushechnikov
    revenue_data = Order.objects.filter(
        event__organizer=request.user.organizer_profile
    ).aggregate(total=Sum(F("items__unit_price") * F("items__quantity")))
    total_turnover = revenue_data["total"] or 0

    #man skal kunne søke gjennom sine egne arrangementer
    # Søk
    search_query = request.GET.get("search", "")
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(venue__name__icontains=search_query)
            | Q(venue__address__city__icontains=search_query)
        )

    # Sortering
    sort_by = request.GET.get("sort", "date_asc")

    if sort_by == "date_asc":
        events = events.order_by("start_datetime")
    elif sort_by == "date_desc":
        events = events.order_by("-start_datetime")
    elif sort_by == "title_asc":
        events = events.order_by("title")
    elif sort_by == "title_desc":
        events = events.order_by("-title")
    elif sort_by == "venue":
        events = events.order_by("venue__name")

    status = request.GET.get("status", "active")

    now = timezone.now()

    if status == "active":
        events = events.filter(end_datetime__gte=now)
    elif status == "past":
        events = events.filter(end_datetime__lt=now)
    elif status == "all":
        events = events

    # Paginering - 12 arrangementer per side
    paginator = Paginator(events, 4)
    page = request.GET.get("page")

    try:
        events_page = paginator.page(page)
    except PageNotAnInteger:
        # Hvis side ikke er et heltall, vis første side
        events_page = paginator.page(1)
    except EmptyPage:
        # Hvis side er utenfor rekkevidde, vis siste side
        events_page = paginator.page(paginator.num_pages)


    context = {
        "organizer": organizer,
        "organizer_form": organizer_form,

        #stats
        "total_events": total_events,
        "active_events": active_events,

        "events": events_page,
        "search_query": search_query,
        "sort_by": sort_by,
        "filtered_count": paginator.count, #antall etter filter
        "status": status,
        
        "sold_tickets": sold_tickets,
        "total_turnover": total_turnover,
    }

    return render(request, "users/organizer_profile.html", context)
