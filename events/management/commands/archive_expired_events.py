"""
Management command for arkivering av avsluttede arrangementer
Kjøring: python manage.py archive_expired_events
Bidrag til denne filen: Nikita Pushechnikov
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, Count, F
from django.db import transaction
from events.models import Event, ArchivedEvent, ArchivedEventImage
from tickets.models import Order, Ticket


class Command(BaseCommand):
    help = (
        "Arkiverer avsluttede arrangementer (konserter/festivaler) i en separat tabell"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=0,
            help="Arkiver arrangementer som ble avsluttet for N dager siden (standard 0 - rett etter avslutning)",
        )

    def handle(self, *args, **options):
        days_ago = options["days"]
        cutoff_date = timezone.now() - timezone.timedelta(days=days_ago)

        # Finn alle arrangementer som allerede er avsluttet
        expired_events = Event.objects.filter(end_datetime__lt=cutoff_date)

        if not expired_events.exists():
            self.stdout.write(self.style.SUCCESS("Ingen arrangementer å arkivere"))
            return

        archived_count = 0

        for event in expired_events:
            try:
                with transaction.atomic():
                    # Beregn statistikk
                    total_tickets = Ticket.objects.filter(
                        ticket_type__event=event
                    ).count()

                    # Beregn total inntekt: sum av (enhetspris × antall) for alle ordrelinjer
                    total_revenue = (
                        Order.objects.filter(event=event).aggregate(
                            total=Sum(F("items__unit_price") * F("items__quantity"))
                        )["total"]
                        or 0
                    )

                    # Hent liste over artister
                    performers_list = ", ".join(
                        [p.name for p in event.performers.all()]
                    )

                    # Opprett arkivoppføring
                    archived_event = ArchivedEvent.objects.create(
                        original_event_id=event.id,
                        organizer_name=(
                            event.organizer.organization_name
                            if hasattr(event.organizer, "organization_name")
                            else str(event.organizer)
                        ),
                        venue_name=event.venue.name,
                        venue_address=str(event.venue.address),
                        title=event.title,
                        description=event.description,
                        performers_list=performers_list,
                        event_type=event.event_type,
                        start_datetime=event.start_datetime,
                        end_datetime=event.end_datetime,
                        created_at=event.created_at,
                        slug=event.slug,
                        total_tickets_sold=total_tickets,
                        total_revenue=total_revenue,
                    )

                    # Arkiver bilder
                    for image in event.images.all():
                        ArchivedEventImage.objects.create(
                            archived_event=archived_event,
                            image_path=image.image.name if image.image else "",
                            alt_text=image.alt_text,
                            is_cover=image.is_cover,
                        )

                    # Marker arrangementet som arkivert (ikke slett, for å bevare ordrehistorikk)
                    event.is_archived = True
                    event.save()

                    archived_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Arkivert: {event.title} "
                            f"(billetter: {total_tickets}, inntekt: {total_revenue} kr)"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Feil ved arkivering av arrangement "{event.title}": {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f"Fullført: arkivert {archived_count} av {expired_events.count()} arrangementer"
            )
        )
