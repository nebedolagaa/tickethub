"""
Bidratt til denne filen:
    - Kamilla Nizamova
"""

from django.db import models
from django.core.validators import MinValueValidator

from django.db.models import Q, F
from django.db.models.functions import Coalesce
from django.utils.text import slugify
from django.urls import reverse


# Create your models here.
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(
        max_length=100, default="Norway"
    )  # prosjektet er i Norge, dersom i fremtiden den blir internasjonal kan dette feltet endres og en ny tabell for land kan lages

    def __str__(self):
        return f"{self.street}, {self.postal_code} {self.city}"

    class Meta:
        verbose_name_plural = "Addresses"


# Modell for byer med bilder
class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Bynavn")
    image_url = models.URLField(max_length=500, blank=True, verbose_name="Bilde-URL")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["name"]


# tabell for location/venue av en arrangement
class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="venues"
    )

    def __str__(self):
        return self.name


# en lokasjon kan ha flere areas for arrangement
# VenueArea representerer en fysisk sone på en arena (f.eks. parkett, balkong,
# ståplass eller VIP-område).

# Denne modellen er statisk og beskriver kun den faste utformingen av lokalet og er uavhengig
# av arrangementer og billettsalg.

# Pris, billettype og tilgjengelighet håndteres i TicketType-modellen,
# som er knyttet til et spesifikt arrangement (Event)


class VenueArea(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="areas")
    name = models.CharField(max_length=100)
    max_capacity_total = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], blank=False, null=False
    )
    max_capacity_seated = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], blank=True, null=True
    )
    max_capacity_standing = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], blank=True, null=True
    )

    def __str__(self):
        return f"{self.venue.name} - {self.name}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    # max_capacity_total må være større eller lik
                    # (sitteplasser + ståplasser), der NULL behandles som 0
                    max_capacity_total__gte=(
                        Coalesce(F("max_capacity_seated"), 0)
                        + Coalesce(F("max_capacity_standing"), 0)
                    )
                ),
                # dersom betingelsen ikke er oppfylt blir det lettere å finne hvor feilen er
                # feks: IntegrityError: CHECK constraint failed: capacity_not_exceed_total
                # navnet på constrainten vises i feilmeldingen
                name="capacity_not_exceed_total",
            ),
            models.UniqueConstraint(
                fields=["venue", "name"], name="unique_venue_area_name"
            ),
        ]

class Event(models.Model):
    # Valgmuligheter for arrangementstype
    EVENT_TYPE_CHOICES = [
        ("concert", "Konsert"),
        ("festival", "Festival"),
    ]

    organizer = models.ForeignKey(
        "users.OrganizerProfile", on_delete=models.CASCADE, related_name="events"
    )
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    performers = models.ManyToManyField(Performer, blank=True, related_name="events")

    # Type arrangement - konsert eller festival
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default="concert",
        artists = models.ManyToManyField('Artist', blank=True, related_name='events') #JF- knytte spesifikk artist til arrangement 
        help_text="Type arrangement: konsert eller festival",
    )

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    # Slug brukes i URL-er (f.eks. /events/oslo-jazz-festival/)
    # den er ikke unique fordi id brukes i tillegg til slug og garanterer entydighet
    slug = models.SlugField(max_length=255, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Hvis slug ikke er satt, lager vi en automatisk basert på tittel.
        # Slug trenger ikke være unik fordi primærnøkkel (pk) brukes i URL
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # Returnerer den offisielle URL-en til arrangementet.
        # Bruker både pk og slug, der pk sikrer entydighet og slug gir lesbarhet.
        return reverse("event_detail", kwargs={"pk": self.pk, "slug": self.slug})


# For å støtte flere bilder per arrangement og gjøre modellen mer fleksibel og skalerbar
# lager vi en modell for bilder knyttet til arrangementer
class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="event_images/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_cover = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event.title} - image"


# i neste class skal vi lage static rows and seats som er knyttet til VenueArea
class Row(models.Model):
    venue_area = models.ForeignKey(
        VenueArea, on_delete=models.CASCADE, related_name="rows"
    )
    name = models.CharField(max_length=20)  # feks A, B, C

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["venue_area", "name"], name="unique_row_in_venue_area"
            ),
        ]


class Seat(models.Model):
    row = models.ForeignKey(Row, on_delete=models.CASCADE, related_name="seats")
    number = models.PositiveIntegerField()  # 1, 2, 3...

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "number"], name="unique_seat_in_row"
            ),
        ]


# modellen som reserverer et sete for én event dette er KUN sitteplasser
# ståplasser skal selges som et antall.
class EventSeat(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_seats"
    )
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, related_name="event_seats")
    is_sold = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "seat"], name="unique_seat_per_event"
            ),
        ]


# for ståplasser trenger vi en modell som holder styr på hvor mange ståplasser som er solgt for hver VenueArea i et arrangement
class EventStandingAllocation(models.Model):
    event = models.ForeignKey(
        "events.Event", on_delete=models.CASCADE, related_name="standing_allocations"
    )
    venue_area = models.ForeignKey(
        "events.VenueArea",
        on_delete=models.PROTECT,
        related_name="standing_allocations",
    )

    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    sold = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "venue_area"],
                name="unique_standing_allocation_per_event_area",
            ),
        ]

    def __str__(self):
        return f"{self.event.title} / {self.venue_area.name} standing: {self.sold}/{self.capacity}"

    @property
    def remaining(self):
        return self.capacity - self.sold

class Performer(models.Model):
    name=models.CharField(max_length=255, unique=True)
    slug=models.SlugField(max_length=255, unique=True)
    bio=models.TextField(blank=True)
    genre=models.CharField(max_length=20, blank=True)
    image=models.ImageField(upload_to='performers/', blank=True, null=True)
    website= models.URLField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def save(self, *args,**kwargs):
        if not self.slug:
            base=slugify(self.name)[:240]
            slug= base
            i=1
            while performer.objects.filter(slug=slug).exists():
                slug=f"{base}-{i}"
                i=i+1
            self.slug=slug
        super().save(*args,**kwargs)

    def display_name(self):
        return self.name

    def get_absolute_url(self):
        try:
            return reverse("performer_detail", args={"slug": self.slug})
        except:
            return'#' #faller tilbake til tom lenke hvis feil.

    def __str__(self):
        return self.name

