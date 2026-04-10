from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Event, Venue, Address
from users.models import OrganizerProfile

# Create your tests here.


class EventAPITestCase(APITestCase):
    def setUp(self):
        # Opprett testdata
        User = get_user_model()
        self.user = User.objects.create_user(
            first_name='Test', last_name='User', email='test@example.com', password='testpass'
        )
        self.organizer = OrganizerProfile.objects.create(user=self.user, organization_name='Test Org')
        self.address = Address.objects.create(street='Test Street', city='Test City', postal_code='1234', country='Norway')
        self.venue = Venue.objects.create(name='Test Venue', address=self.address)
        self.event = Event.objects.create(
            organizer=self.organizer,
            venue=self.venue,
            title='Test Event',
            description='Test Description',
            start_datetime='2024-12-01T10:00:00Z',
            end_datetime='2024-12-01T12:00:00Z'
        )
    """Delvis update av event"""
    def test_update_event_partial(self):
        self.client.login(username=self.user.email, password='testpass')
        url = reverse('event-update-api', kwargs={'pk': self.event.pk})
        data = {'title': 'Updated Event Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Event Title')

    """Full oppdatering av event"""
    def test_update_event_full(self):
        self.client.login(username=self.user.email, password='testpass')
        url = reverse('event-update-api', kwargs={'pk': self.event.pk})
        
        data = {
            'organizer': self.organizer.pk,
            'venue': self.venue.pk,
            'title': 'Fully Updated Event',
            'description': 'Updated Description',
            'start_datetime': '2024-12-02T10:00:00Z',
            'end_datetime': '2024-12-02T12:00:00Z'
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK )
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Fully Updated Event')

    """Tester oppdateringer av ikke-eksisterende event"""
    def test_update_event_not_found(self):
        self.client.login(username=self.user.email, password='testpass')
        url = reverse('event-update-api', kwargs={'pk': 999})
        data = {'title': 'New Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
