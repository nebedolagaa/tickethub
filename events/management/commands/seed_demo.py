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
            ("Stavanger Konserthus", "Sandvigå 1", "4007", "Stavanger"),
            ("USF Verftet", "Georgernes verft 12", "5011", "Bergen"),
        ]:
            v = Venue.objects.create(name=name, address=Address.objects.create(street=street, postal_code=pc, city=city))
            VenueArea.objects.create(venue=v, name="Parkett", max_capacity_total=2000, max_capacity_standing=2000)
            VenueArea.objects.create(venue=v, name="Balkong", max_capacity_total=500, max_capacity_seated=500)
            venues.append(v)

        performers = {}
        for name, genre in [("The Fjord Lights", "rock"), ("Aurora Hansen", "pop"), ("Midnight Jazz Trio", "jazz"),
                            ("Nordic Beats", "electronic"), ("Bergen Philharmonic Demo", "classical"), ("Lofoten Folk", "folk"),
                            ("Glacier", "metal"), ("Oda & The Waves", "pop"), ("Lil Troll", "hiphop"),
                            ("Polar Soul Collective", "r&b"), ("Svalbard Sound", "electronic"), ("Hardanger Strings", "classical")]:
            performers[name] = Performer.objects.create(name=name, genre=genre, bio=f"{name} er et fiktivt demo-band for TicketHub.")

        # bilder ligger i media/images/demo og kopieres til event_images slik som ved vanlig opplasting
        img_dir = Path(settings.MEDIA_ROOT) / "event_images"
        img_dir.mkdir(parents=True, exist_ok=True)
        src = sorted((Path(settings.MEDIA_ROOT) / "images" / "demo").glob("*.jpg"))
        for s in src:
            shutil.copy(s, img_dir / s.name)

        # (tittel, type, lokasjon, dager fra i dag, artister, pris)
        events = [
            ("The Fjord Lights: Europe Tour", "concert", 0, 12, ["The Fjord Lights"], 549),
            ("Aurora Hansen: Northern Nights", "concert", 1, 16, ["Aurora Hansen"], 699),
            ("Oslo Summer Festival", "festival", 3, 21, ["Nordic Beats", "The Fjord Lights", "Aurora Hansen"], 1290),
            ("Midnight Jazz Trio Live", "concert", 2, 25, ["Midnight Jazz Trio"], 399),
            ("Glacier: Frozen Tour", "concert", 5, 28, ["Glacier"], 489),
            ("Oda & The Waves", "concert", 4, 33, ["Oda & The Waves"], 429),
            ("Lil Troll: Fjellet Tour", "concert", 0, 37, ["Lil Troll"], 599),
            ("Bergen Classical Evening", "concert", 1, 41, ["Bergen Philharmonic Demo", "Hardanger Strings"], 450),
            ("Polar Soul Night", "concert", 3, 45, ["Polar Soul Collective"], 379),
            ("Svalbard Sound: Live", "concert", 5, 50, ["Svalbard Sound"], 459),
            ("Bergen Beats Festival", "festival", 5, 54, ["Nordic Beats", "Svalbard Sound", "Lil Troll"], 1190),
            ("Hardanger Strings", "concert", 4, 58, ["Hardanger Strings"], 349),
            ("Trondheim Rock Weekend", "festival", 2, 63, ["Glacier", "The Fjord Lights"], 1090),
            ("Lofoten Folk Festival", "festival", 2, 70, ["Lofoten Folk", "Midnight Jazz Trio"], 990),
            ("Aurora Hansen: Winter Songs", "concert", 0, 78, ["Aurora Hansen"], 749),
            ("Stavanger Jazz Days", "festival", 4, 85, ["Midnight Jazz Trio", "Polar Soul Collective"], 890),
            ("Nordic Beats: Club Night", "concert", 3, 92, ["Nordic Beats"], 299),
            ("Julekonsert med Hardanger Strings", "concert", 1, 99, ["Hardanger Strings", "Lofoten Folk"], 399),
        ]
        for i, (title, etype, vi, days, perf, price) in enumerate(events):
            start = now + timedelta(days=days, hours=19 - now.hour)
            end = start + (timedelta(days=2) if etype == "festival" else timedelta(hours=3))
            e = Event.objects.create(
                organizer=org, venue=venues[vi], title=title, event_type=etype, start_datetime=start, end_datetime=end,
                description=f"{title}. En uforglemmelig kveld med levende musikk. (Demo-arrangement)",
            )
            e.performers.set([performers[p] for p in perf])
            EventImage.objects.create(event=e, image=f"event_images/{src[i % len(src)].name}", alt_text=title, is_cover=True)
            parkett, balkong = venues[vi].areas.order_by("id")
            TicketType.objects.create(event=e, venue_area=parkett, name=TicketType._meta.get_field("name").choices[0][0], price=price, quantity=1500)
            choices = TicketType._meta.get_field("name").choices
            TicketType.objects.create(event=e, venue_area=balkong, name=choices[1 % len(choices)][0], price=price + 300, quantity=300)
            EventStandingAllocation.objects.create(event=e, venue_area=parkett, capacity=1500, sold=100 + (i * 170) % 1300)

        self.stdout.write(self.style.SUCCESS(f"Demo-data lagt inn: {Event.objects.count()} arrangementer"))
