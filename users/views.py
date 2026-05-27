"""
Bidratt til denne filen:
    - Kamilla Nizamova
    - Nikita Pushechnikov
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages, auth
from django.db.models import Sum, F

from django.contrib.auth.decorators import login_required

from .models import Account, UserProfile, OrganizerProfile
from tickets.models import Ticket, Order, TicketType
from events.models import Event, Venue, VenueArea, Performer, Address
from events.forms import EventForm, TicketTypeForm
import json

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
    active_tab = request.GET.get("tab", "profile")
    if active_tab not in {"profile", "tickets"}:
        active_tab = "profile"

    now = timezone.now()

    tickets = Ticket.objects.none()
    tickets_page = None
    tickets_count = Ticket.objects.filter(user=request.user).count()
    upcoming_events = (
        Ticket.objects.filter(
            user=request.user,
            ticket_type__event__end_datetime__gte=now,
        )
        .values("ticket_type__event")
        .distinct()
        .count()
    )

    if active_tab == "tickets":
        tickets_queryset = (
            Ticket.objects.filter(user=request.user)
            .select_related(
                "ticket_type",
                "ticket_type__event",
                "ticket_type__event__venue",
                "ticket_type__event__venue__address",
                "event_seat__seat",
            )
            .prefetch_related("ticket_type__event__performers")
            .order_by("-ticket_type__event__start_datetime")
        )

        paginator = Paginator(tickets_queryset, 6)
        page_number = request.GET.get("page")
        tickets_page = paginator.get_page(page_number)
        tickets = tickets_page.object_list

        for ticket in tickets:
            ticket.is_active = ticket.ticket_type.event.end_datetime >= now

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
        "totaly_used": totaly_used,
        "tickets_count": tickets_count,
        "tickets": tickets,
        "tickets_page": tickets_page,
        "upcoming_events": upcoming_events,
        "active_tab": active_tab,
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

    # man skal kunne søke gjennom sine egne arrangementer
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

    # statistikk for solgte billetter og total omsetning per arrangementer
    # using two loops to get through each event and then through each ticket type for that event
    # because there are several ticket types per event
    for event in events_page:
        ticket_types = TicketType.objects.filter(event=event)

        total_tickets = 0
        sold_count = 0
        income_per_event = 0

        for ticket_type in ticket_types:
            total_tickets += ticket_type.quantity
            sold_for_type = ticket_type.tickets.count()
            sold_count += sold_for_type
            income_per_event += sold_for_type * ticket_type.price

        sold_percent = (sold_count / total_tickets) * 100 if total_tickets > 0 else 0

        event.total_tickets = total_tickets
        event.sold_count = sold_count
        event.sold_percent = sold_percent
        event.income_per_event = income_per_event
        event.status_label = "Aktiv" if event.end_datetime >= now else "Avsluttet"
        event.status_class = (
            "NP-badge--active"
            if event.end_datetime >= now
            else "NP-badge--expired"
        )

    context = {
        "organizer": organizer,
        "organizer_form": organizer_form,
        # stats
        "total_events": total_events,
        "active_events": active_events,
        "events": events_page,
        "search_query": search_query,
        "sort_by": sort_by,
        "filtered_count": paginator.count,  # antall etter filter
        "status": status,
        "sold_tickets": sold_tickets,
        "total_turnover": total_turnover,
    }

    return render(request, "users/organizer_profile.html", context)


@login_required
def create_event(request):
    """Side for å opprette et nytt arrangement (kun for arrangører)"""
    try:
        organizer = OrganizerProfile.objects.get(user=request.user)
    except OrganizerProfile.DoesNotExist:
        messages.error(request, "Du har ikke tilgang til å opprette arrangementer.")
        return redirect("users:user_profile")

    venues = Venue.objects.all().prefetch_related("areas")
    venue_areas = {}
    for venue in venues:
        venue_areas[venue.id] = [
            {"id": area.id, "name": area.name} for area in venue.areas.all()
        ]

    if request.method == "POST":
        event_form = EventForm(request.POST)
        ticket_form = TicketTypeForm(request.POST)

        venue_mode = request.POST.get("venue_mode", "existing")  # existing | new

        # ── Ny lokasjon ──
        new_venue_obj = None
        new_venue_area_obj = None
        venue_errors = []
        if venue_mode == "new":
            nv_name = request.POST.get("nv_name", "").strip()
            nv_street = request.POST.get("nv_street", "").strip()
            nv_city = request.POST.get("nv_city", "").strip()
            nv_postal = request.POST.get("nv_postal", "").strip()
            nv_capacity = request.POST.get("nv_capacity", "").strip()
            if not nv_name:
                venue_errors.append("Lokasjonsnavn er påkrevd.")
            if not nv_street:
                venue_errors.append("Gateadresse er påkrevd.")
            if not nv_city:
                venue_errors.append("By er påkrevd.")
            if not nv_postal:
                venue_errors.append("Postnummer er påkrevd.")
            if nv_capacity:
                try:
                    nv_capacity = int(nv_capacity)
                    if nv_capacity < 1:
                        venue_errors.append("Kapasitet må være minst 1.")
                except ValueError:
                    venue_errors.append("Kapasitet må være et tall.")
            else:
                venue_errors.append("Kapasitet er påkrevd.")
            # Sjekk om lokasjon med samme navn allerede finnes
            if nv_name and not venue_errors:
                existing_venue = Venue.objects.filter(name__iexact=nv_name).first()
                if existing_venue:
                    venue_errors.append(
                        f'En lokasjon med navnet "{existing_venue.name}" finnes allerede. '
                        f"Velg den fra listen over eksisterende lokasjoner i stedet."
                    )

        # ── Ny artist ──
        new_performer_name = request.POST.get("new_performer_name", "").strip()
        new_performer_genre = request.POST.get("new_performer_genre", "other").strip()
        new_performer = None
        performer_warning = None
        should_create_performer = False
        if new_performer_name:
            existing = Performer.objects.filter(name__iexact=new_performer_name).first()
            if existing:
                performer_warning = f'"{existing.name}" finnes allerede i systemet og ble lagt til arrangementet.'
                new_performer = existing
            else:
                should_create_performer = True

        forms_valid = event_form.is_valid() and ticket_form.is_valid()

        # Legg til venue-feil i event_form
        if (
            venue_mode == "existing"
            and forms_valid
            and not event_form.cleaned_data.get("venue")
        ):
            event_form.add_error("venue", "Velg en lokasjon.")
            forms_valid = False

        if (
            venue_mode == "existing"
            and forms_valid
            and not ticket_form.cleaned_data.get("venue_area")
        ):
            ticket_form.add_error("venue_area", "Velg en sone.")
            forms_valid = False

        if forms_valid and not venue_errors:
            with transaction.atomic():
                event = event_form.save(commit=False)
                event.organizer = organizer

                if venue_mode == "new":
                    address = Address.objects.create(
                        street=nv_street,
                        city=nv_city,
                        postal_code=nv_postal,
                    )
                    new_venue_obj = Venue.objects.create(name=nv_name, address=address)
                    new_venue_area_obj = VenueArea.objects.create(
                        venue=new_venue_obj,
                        name="Generell",
                        max_capacity_total=nv_capacity,
                    )
                    event.venue = new_venue_obj

                if should_create_performer:
                    new_performer = Performer.objects.create(
                        name=new_performer_name,
                        genre=new_performer_genre or "other",
                    )

                event.save()
                event_form.save_m2m()
                if new_performer:
                    event.performers.add(new_performer)

                ticket = ticket_form.save(commit=False)
                ticket.event = event
                if venue_mode == "new":
                    ticket.venue_area = new_venue_area_obj
                ticket.save()

            if performer_warning:
                messages.warning(request, performer_warning, extra_tags="event")
            messages.success(
                request, "Arrangementet ble opprettet!", extra_tags="event"
            )
            return redirect("users:organizer_profile")
    else:
        event_form = EventForm()
        ticket_form = TicketTypeForm()
        venue_errors = []
        performer_warning = None

    context = {
        "event_form": event_form,
        "ticket_form": ticket_form,
        "venue_areas_json": json.dumps(venue_areas),
        "genre_choices": Performer.GENRE_CHOICES,
        "venue_errors": venue_errors if request.method == "POST" else [],
        "performer_warning": performer_warning if request.method == "POST" else None,
        "venue_mode_post": (
            request.POST.get("venue_mode", "existing")
            if request.method == "POST"
            else "existing"
        ),
    }
    return render(request, "users/create_event.html", context)


@login_required
def edit_event(request, event_id):
    # Rediger arrangementsinformasjon og legg eventuelt til en ny billettype.
    try:
        organizer = OrganizerProfile.objects.get(user=request.user)
    except OrganizerProfile.DoesNotExist:
        # Hvis brukeren ikke er arrangør, vis feilmelding og omdiriger til brukerprofilen
        messages.error(request, "Du har ikke tilgang til å redigere arrangementer.")
        return redirect("users:user_profile")

    event = get_object_or_404(Event, id=event_id, organizer=organizer)

    if request.method == "POST":
        event_form = EventForm(request.POST, instance=event)
        add_ticket_type = request.POST.get("add_ticket_type") == "1"
        new_ticket_form = TicketTypeForm(request.POST if add_ticket_type else None)
        new_ticket_form.fields["venue_area"].queryset = event.venue.areas.all()

        # Hent eventuell ny artist skrevet inn manuelt
        new_performer_name = request.POST.get("new_performer_name", "").strip()
        new_performer_genre = request.POST.get("new_performer_genre", "other").strip()

        # Standardverdier for ny artist
        new_performer = None
        performer_warning = None
        should_create_performer = False

        if new_performer_name:
            existing = Performer.objects.filter(name__iexact=new_performer_name).first()
            if existing:
                performer_warning = f'"{existing.name}" finnes allerede i systemet og ble lagt til arrangementet.'
                new_performer = existing
            else:
                should_create_performer = True

        event_valid = event_form.is_valid()
        ticket_valid = not add_ticket_type or new_ticket_form.is_valid()

        if add_ticket_type and event_valid and ticket_valid:
            if not new_ticket_form.cleaned_data.get("venue_area"):
                new_ticket_form.add_error("venue_area", "Velg en sone.")
                ticket_valid = False

        if event_valid and ticket_valid:
            # Sikrer at alle databaseoperasjoner fullføres samlet, og at ingen endringer blir lagret hvis noe går galt underveis
            with transaction.atomic():
                event = event_form.save()

                # Opprett ny artist hvis nødvendig
                if should_create_performer:
                    new_performer = Performer.objects.create(
                        name=new_performer_name,
                        genre=new_performer_genre or "other",
                    )

                # Legg artist til arrangemente
                if new_performer:
                    event.performers.add(new_performer)

                if add_ticket_type:
                    new_ticket_type = new_ticket_form.save(commit=False)
                    new_ticket_type.event = event
                    new_ticket_type.save()

            if performer_warning:
                messages.warning(request, performer_warning, extra_tags="event")
            messages.success(
                request, "Arrangementet ble oppdatert!", extra_tags="event"
            )
            return redirect("users:organizer_profile")
    else:
        event_form = EventForm(instance=event)
        new_ticket_form = TicketTypeForm()
        new_ticket_form.fields["venue_area"].queryset = event.venue.areas.all()
        add_ticket_type = False
        performer_warning = None

    context = {
        "event": event,
        "event_form": event_form,
        "new_ticket_form": new_ticket_form,
        "ticket_types": event.ticket_types.select_related("venue_area").all(),
        "add_ticket_type": add_ticket_type,
        "genre_choices": Performer.GENRE_CHOICES,
        "performer_warning": performer_warning if request.method == "POST" else None,
    }
    return render(request, "users/edit_event.html", context)
