from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

#denne modelen viser hva som selges for en bestemt event
#for eksempel: billettype, forksjellig pris, kapasitet kontroll, forksjellige zones med priser som varierer 
class TicketType(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='ticket_types')
    venue_area = models.ForeignKey('events.VenueArea', on_delete=models.PROTECT, related_name='ticket_types')
    name = models.CharField(max_length=100) # f. eks. "Ordinær", "VIP", "Student"
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)]) #antall biletter tilgjengelig for denne typen

    def __str__(self):
        return f"{self.event.title} - {self.name}"


#denne modelen representerer en faktisk billett som er kjøpt av en kunde
class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT, related_name='tickets')

    #kun for sitte plasser
    event_seat = models.OneToOneField("events.EventSeat", on_delete=models.PROTECT, null=True, blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket for {self.ticket_type.event.title} - {self.ticket_type.name} (User: {self.user.username})"
    

#neste modell representerer et kjøp av flere billetter i en transaksjon
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')

    #det skal være mulig å ha flere biletter, men KUN for EN event per ordre
    event = models.ForeignKey('events.Event', on_delete=models.PROTECT, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} for {self.event.title}"
    

#denne modellen representerer en linje i en ordre, dvs en billettype og antall billetter av denne typen
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT, related_name='order_items')

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    #pris ved kjøpstidspunktet (lagres har for historikk, i tilfelle prisendringer senere)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"OrderItem: {self.quantity} x {self.ticket_type.name} for Order #{self.order.id}"
    

#denne modellen representerer en spesifikk sitteplass knyttet til en ordrelinje uten den hvet vi ikker hvilke seter som er solgt
class OrderSeat(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="seats")

    # OneToOne: samme EventSeat kan ikke ligge i flere ordre samtidig
    event_seat = models.OneToOneField("events.EventSeat", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.order_item} -> {self.event_seat}"