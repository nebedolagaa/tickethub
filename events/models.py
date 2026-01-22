from django.db import models
from django.core.validators import MinValueValidator


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
    address = models.ForeignKey(Address, on_delete=models.PROTECT)

    def __str__(self):
        return self.name
    
#en lokasjon kan ha flere areas for arrangement 
class VenueArea(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    max_capacity_total = models.IntegerField(validators=[MinValueValidator(1)], blank = False, null = False)
    max_capacity_seated = models.IntegerField(validators=[MinValueValidator(0)], blank = True, null = True)
    max_capacity_standing = models.IntegerField(validators=[MinValueValidator(0)], blank = True, null = True)

    def __str__(self):
        return f"{self.venue.name} - {self.name}" 
    