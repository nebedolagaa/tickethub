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


# Nikita Pushechnikov - tester for POST /api/concerts/
class ConcertCreateAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            first_name="Test",
            last_name="User",
            email="concert@example.com",
            password="testpass",
        )
        self.organizer = OrganizerProfile.objects.create(
            user=self.user, organization_name="Concert Org"
        )
        self.address = Address.objects.create(
            street="Concert St", city="Oslo", postal_code="0150", country="Norway"
        )
        self.venue = Venue.objects.create(name="Concert Hall", address=self.address)
        self.url = reverse("concert-list-api")

    def test_create_concert_success(self):
        """Opprette konsert med alle obligatoriske felt"""
        data = {
            "organizer": self.organizer.pk,
            "venue": self.venue.pk,
            "title": "Ny Konsert",
            "start_datetime": "2027-06-01T18:00:00Z",
            "end_datetime": "2027-06-01T22:00:00Z",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Ny Konsert")
        self.assertEqual(response.data["slug"], "ny-konsert")

    def test_create_concert_sets_event_type_concert(self):
        """event_type skal alltid settes til concert"""
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

    def test_create_concert_missing_required_fields(self):
        """Manglende obligatoriske felt skal gi 400"""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertIn("organizer", response.data)
        self.assertIn("venue", response.data)
        self.assertIn("start_datetime", response.data)
        self.assertIn("end_datetime", response.data)

    def test_create_concert_end_before_start(self):
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

    def test_create_concert_end_equal_start(self):
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


# --------------------------------------------------------------------------
