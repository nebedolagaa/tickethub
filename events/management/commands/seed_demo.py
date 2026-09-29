"""
Lager demo-data slik at man kan teste nettsiden lokalt uten en ferdig database.
Kjøres med: python manage.py seed_demo

Demo-brukere (passord: demo12345):
    - organizer@example.com  (arrangør)
    - ola@example.com        (vanlig bruker)
"""

from datetime import timedelta
import shutil
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from events.models import Address, City, Venue, VenueArea, Event, EventImage, Performer, EventStandingAllocation
from tickets.models import TicketType
from users.models import Account, OrganizerProfile, UserProfile

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Legger inn demo-arrangementer, lokasjoner og brukere"

    def handle(self, *args, **options):
        if Account.objects.filter(email="organizer@example.com").exists():
            raise CommandError("Demo-data finnes allerede")

        now = timezone.now().replace(minute=0, second=0, microsecond=0)

        org_user = Account.objects.create_user("Demo", "Arrangør", "organizer@example.com", "demo12345")
        org = OrganizerProfile.objects.create(
            user=org_user, organization_name="Nordlys Events AS", contact_email="post@example.com",
            organization_address="Karl Johans gate 1", organization_postcode="0154", organization_city="Oslo",
        )
        user = Account.objects.create_user("Ola", "Nordmann", "ola@example.com", "demo12345")
        UserProfile.objects.create(user=user, address="Storgata 10", city="Bergen", postal_code="5003", country="Norge")
        UserProfile.objects.create(user=org_user, city="Oslo", country="Norge")

        for name in ["Oslo", "Bergen", "Trondheim", "Stavanger"]:
            City.objects.get_or_create(name=name)

        venues = []
        for name, street, pc, city in [
            ("Oslo Spektrum", "Sonja Henies plass 2", "0185", "Oslo"),
            ("Grieghallen", "Edvard Griegs plass 1", "5015", "Bergen"),
            ("Olavshallen", "Kjøpmannsgata 44", "7011", "Trondheim"),
            ("Tjuvholmen Scene", "Strandpromenaden 5", "0252", "Oslo"),
        ]:
            v = Venue.objects.create(name=name, address=Address.objects.create(street=street, postal_code=pc, city=city))
            VenueArea.objects.create(venue=v, name="Parkett", max_capacity_total=2000, max_capacity_standing=2000)
            VenueArea.objects.create(venue=v, name="Balkong", max_capacity_total=500, max_capacity_seated=500)
            venues.append(v)

        performers = {}
        for name, genre in [("The Fjord Lights", "rock"), ("Aurora Hansen", "pop"), ("Midnight Jazz Trio", "jazz"),
                            ("Nordic Beats", "electronic"), ("Bergen Philharmonic Demo", "classical"), ("Lofoten Folk", "folk")]:
            performers[name] = Performer.objects.create(name=name, genre=genre, bio=f"{name} er et fiktivt demo-band for TicketHub.")

        img_dir = Path(settings.MEDIA_ROOT) / "event_images"
        img_dir.mkdir(parents=True, exist_ok=True)
        src = [Path(settings.MEDIA_ROOT) / "images" / f for f in ("event-image.jpg", "event-image-2.jpg")]
        for s in src:
            shutil.copy(s, img_dir / s.name)

        events = [
            ("The Fjord Lights – Europe Tour", "concert", 0, 12, ["The Fjord Lights"], 549),
            ("Aurora Hansen: Northern Nights", "concert", 1, 20, ["Aurora Hansen"], 699),
            ("Oslo Summer Festival", "festival", 3, 30, ["Nordic Beats", "The Fjord Lights", "Aurora Hansen"], 1290),
            ("Midnight Jazz Trio Live", "concert", 2, 40, ["Midnight Jazz Trio"], 399),
            ("Bergen Classical Evening", "concert", 1, 55, ["Bergen Philharmonic Demo"], 450),
            ("Lofoten Folk Festival", "festival", 2, 70, ["Lofoten Folk", "Midnight Jazz Trio"], 990),
        ]
        for i, (title, etype, vi, days, perf, price) in enumerate(events):
            start = now + timedelta(days=days, hours=19 - now.hour)
            end = start + (timedelta(days=2) if etype == "festival" else timedelta(hours=3))
            e = Event.objects.create(
                organizer=org, venue=venues[vi], title=title, event_type=etype, start_datetime=start, end_datetime=end,
                description=f"{title} – en uforglemmelig kveld med levende musikk. (Demo-arrangement)",
            )
            e.performers.set([performers[p] for p in perf])
            EventImage.objects.create(event=e, image=f"event_images/{src[i % 2].name}", alt_text=title, is_cover=True)
            parkett, balkong = venues[vi].areas.order_by("id")
            TicketType.objects.create(event=e, venue_area=parkett, name=TicketType._meta.get_field("name").choices[0][0], price=price, quantity=1500)
            choices = TicketType._meta.get_field("name").choices
            TicketType.objects.create(event=e, venue_area=balkong, name=choices[1 % len(choices)][0], price=price + 300, quantity=300)
            EventStandingAllocation.objects.create(event=e, venue_area=parkett, capacity=1500, sold=300 + i * 90)

        self.stdout.write(self.style.SUCCESS(f"Demo-data lagt inn: {Event.objects.count()} arrangementer"))
