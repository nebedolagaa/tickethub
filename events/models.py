#Folk som kodet her: Kamilla

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
    country = models.CharField(max_length=100, default = 'Norway') #prosjektet er i Norge, dersom i fremtiden den blir internasjonal kan dette feltet endres og en ny tabell for land kan lages

    def __str__(self):
        return f"{self.street}, {self.postal_code} {self.city}"
    

    class Meta:
        verbose_name_plural = 'Addresses'


#tabell for location/venue av en arrangement
class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name = 'venues')

    def __str__(self):
        return self.name
    

#en lokasjon kan ha flere areas for arrangement 
# VenueArea representerer en fysisk sone på en arena (f.eks. parkett, balkong,
# ståplass eller VIP-område).

# Denne modellen statisk og beskriver kun den faste utformingen av lokalet og er uavhengig
# av arrangementer og billettsalg.

# Pris, billettype og tilgjengelighet håndteres i TicketType-modellen,
# som er knyttet til et spesifikt arrangement (Event)

class VenueArea(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name = 'areas')
    name = models.CharField(max_length=100)
    max_capacity_total = models.IntegerField(validators=[MinValueValidator(1)], blank = False, null = False)
    max_capacity_seated = models.IntegerField(validators=[MinValueValidator(0)], blank = True, null = True)
    max_capacity_standing = models.IntegerField(validators=[MinValueValidator(0)], blank = True, null = True)

    def __str__(self):
        return f"{self.venue.name} - {self.name}" 
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(
                    # max_capacity_total må være større eller lik
                    # (sitteplasser + ståplasser), der NULL behandles som 0
                    max_capacity_total__gte=(
                        Coalesce(F("max_capacity_seated"), 0) +
                        Coalesce(F("max_capacity_standing"), 0)
                    )
                ),
                # dersom betingelsen ikke er oppfylt blir det lettere å finne hvor feilen er
                #feks: IntegrityError: CHECK constraint failed: capacity_not_exceed_total
                #navnet på constrainten vises i feilmeldingen
                name="capacity_not_exceed_total",
            ),
            models.UniqueConstraint(fields = ['venue', 'name'], name='unique_venue_area_name'),
        ]



class Event(models.Model):
    organizer = models.ForeignKey('users.OrganizerProfile', on_delete=models.CASCADE, related_name='events')
    venue = models.ForeignKey(Venue, on_delete = models.PROTECT, related_name = 'events')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    # Slug brukes i URL-er (f.eks. /events/oslo-jazz-festival/)
    #den er ikke unique fordi id brukes i tillegg til slug og garanterer entydighet
    slug = models.SlugField(max_length=255, blank=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Hvis slug ikke er satt, lager vi en automatisk basert på tittel.
        #Slug trenger ikke være unik fordi primærnøkkel (pk) brukes i URL
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    

    def get_absolute_url(self):
        # Returnerer den offisielle URL-en til arrangementet.
        #Bruker både pk og slug, der pk sikrer entydighet og slug gir lesbarhet.
        return reverse("event_detail", kwargs={"pk": self.pk, "slug": self.slug})
    
    

#For å støtte flere bilder per arrangement og gjøre modellen mer fleksibel og skalerbar
#lager vi en modell for bilder knyttet til arrangementer
class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_cover = models.BooleanField(default=False)
    