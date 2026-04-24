from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Event, Venue, Address
from users.models import OrganizerProfile

# Create your tests here.


# MB OG JF sine tester:
class EventAPITestCase(APITestCase):
    def setUp(self):
        # Opprett testdata
        User = get_user_model()
        self.user = User.objects.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="testpass",
        )
        self.organizer = OrganizerProfile.objects.create(
            user=self.user, organization_name="Test Org"
        )
        self.address = Address.objects.create(
            street="Test Street", city="Test City", postal_code="1234", country="Norway"
        )
        self.venue = Venue.objects.create(name="Test Venue", address=self.address)
        self.event = Event.objects.create(
            organizer=self.organizer,
            venue=self.venue,
            title="Test Event",
            description="Test Description",
            start_datetime="2024-12-01T10:00:00Z",
            end_datetime="2024-12-01T12:00:00Z",
        )

    """Delvis update av event"""

    def test_update_event_partial(self):
        self.client.login(username=self.user.email, password="testpass")
        url = reverse("event-update-api", kwargs={"pk": self.event.pk})
        data = {"title": "Updated Event Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Updated Event Title")

    """Full oppdatering av event"""

    def test_update_event_full(self):
        self.client.login(username=self.user.email, password="testpass")
        url = reverse("event-update-api", kwargs={"pk": self.event.pk})

        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Fully Updated Event",
            "description": "Updated Description",
            "start_datetime": "2024-12-02T10:00:00Z",
            "end_datetime": "2024-12-02T12:00:00Z",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Fully Updated Event")

    """Tester oppdateringer av ikke-eksisterende event"""

    def test_update_event_not_found(self):
        self.client.login(username=self.user.email, password="testpass")
        url = reverse("event-update-api", kwargs={"pk": 999})
        data = {"title": "New Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# --------------------------------------------------------------------------


# Nikita Pushechnikov - tester for POST /api/events/
class EventCreateAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            first_name="Test",
            last_name="User",
            email="event@example.com",
            password="testpass",
        )
        self.organizer = OrganizerProfile.objects.create(
            user=self.user, organization_name="Event Org"
        )
        self.address = Address.objects.create(
            street="Event St", city="Oslo", postal_code="0150", country="Norway"
        )
        self.venue = Venue.objects.create(name="Event Hall", address=self.address)
        self.url = reverse("event-list-api")

    def test_create_event_success(self):
        """Opprette event med alle obligatoriske felt"""
        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Nytt Event",
            "start_datetime": "2027-06-01T18:00:00Z",
            "end_datetime": "2027-06-01T22:00:00Z",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Nytt Event")
        self.assertEqual(response.data["slug"], "nytt-event")

    def test_create_event_sets_default_event_type(self):
        """event_type skal få riktig standardverdi"""
        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Auto Type Test",
            "start_datetime": "2027-07-01T18:00:00Z",
            "end_datetime": "2027-07-01T22:00:00Z",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        from .models import Event

        event = Event.objects.get(pk=response.data["id"])
        self.assertEqual(event.event_type, "concert")

    def test_create_event_missing_required_fields(self):
        """Manglende obligatoriske felt skal gi 400"""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertIn("organizer", response.data)
        self.assertIn("venue", response.data)
        self.assertIn("start_datetime", response.data)
        self.assertIn("end_datetime", response.data)

    def test_create_event_end_before_start(self):
        """end_datetime før start_datetime skal gi 400"""
        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Ugyldig Dato",
            "start_datetime": "2027-06-01T22:00:00Z",
            "end_datetime": "2027-06-01T18:00:00Z",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_datetime", response.data)

    def test_create_event_end_equal_start(self):
        """end_datetime lik start_datetime skal gi 400"""
        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Lik Dato",
            "start_datetime": "2027-06-01T18:00:00Z",
            "end_datetime": "2027-06-01T18:00:00Z",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_event_festival_type(self):
        """Opprette event med event_type=festival"""
        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Sommerfestival",
            "event_type": "festival",
            "start_datetime": "2027-08-01T12:00:00Z",
            "end_datetime": "2027-08-03T23:00:00Z",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event_type"], "festival")

    def test_create_event_concert_type_explicit(self):
        """Opprette event med event_type=concert eksplisitt"""
        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Rock Konsert",
            "event_type": "concert",
            "start_datetime": "2027-09-01T18:00:00Z",
            "end_datetime": "2027-09-01T22:00:00Z",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event_type"], "concert")

    def test_create_event_invalid_event_type(self):
        """Ugyldig event_type skal gi 400"""
        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Ugyldig Type",
            "event_type": "party",
            "start_datetime": "2027-09-01T18:00:00Z",
            "end_datetime": "2027-09-01T22:00:00Z",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("event_type", response.data)


# --------------------------------------------------------------------------
