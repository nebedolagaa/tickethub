import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Address, Event, Venue, VenueArea
from users.models import OrganizerProfile
from .models import Order, Ticket, TicketType


# Tester for handlekurv og betaling: pris og antall skal alltid sjekkes på serveren
class PaymentSecurityTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        org_user = User.objects.create_user("Org", "Test", "org@example.com", "testpass")
        organizer = OrganizerProfile.objects.create(user=org_user, organization_name="Org AS")
        self.user = User.objects.create_user("Kunde", "Test", "kunde@example.com", "testpass")
        venue = Venue.objects.create(
            name="Hall", address=Address.objects.create(street="Gate 1", city="Oslo", postal_code="0150")
        )
        area = VenueArea.objects.create(venue=venue, name="Parkett", max_capacity_total=100)
        start = timezone.now() + timedelta(days=10)
        self.event = Event.objects.create(
            organizer=organizer, venue=venue, title="Konsert",
            start_datetime=start, end_datetime=start + timedelta(hours=3),
        )
        self.vip = TicketType.objects.create(event=self.event, venue_area=area, name="vip", price=800, quantity=3)
        self.client.login(username="kunde@example.com", password="testpass")

    def add_to_cart(self, quantity, price=None):
        item = {"ticket_type_id": self.vip.id, "quantity": quantity, "name": "VIP"}
        if price is not None:
            item["price"] = price
        self.client.post(reverse("tickets:payment"), {"cart": json.dumps({str(self.vip.id): item})})

    def test_price_from_browser_is_ignored(self):
        self.add_to_cart(2, price=1)
        self.client.post(reverse("tickets:confirm_payment"))
        item = Order.objects.get(user=self.user).items.get()
        self.assertEqual(item.unit_price, 800)
        self.assertEqual(Ticket.objects.filter(user=self.user).count(), 2)

    def test_cannot_buy_more_than_available(self):
        Ticket.objects.create(user=self.user, ticket_type=self.vip)
        self.add_to_cart(3)  # bare 2 igjen
        self.client.post(reverse("tickets:confirm_payment"))
        self.assertFalse(Order.objects.exists())
        self.assertEqual(Ticket.objects.count(), 1)

    def test_invalid_quantity_is_dropped(self):
        for quantity in (0, -5, 11, "abc"):
            self.add_to_cart(quantity)
            self.assertEqual(self.client.session.get("cart"), {})

    def test_cannot_buy_tickets_to_finished_event(self):
        self.event.end_datetime = timezone.now() - timedelta(hours=1)
        self.event.start_datetime = self.event.end_datetime - timedelta(hours=3)
        self.event.save()
        self.add_to_cart(1)
        self.client.post(reverse("tickets:confirm_payment"))
        self.assertFalse(Order.objects.exists())

    def test_confirm_payment_requires_post(self):
        self.add_to_cart(1)
        self.client.get(reverse("tickets:confirm_payment"))
        self.assertFalse(Order.objects.exists())

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()
        response = self.client.post(reverse("tickets:confirm_payment"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
