''' 
Bidratt til denne filen:
    - Kamilla Nizamova
'''
from django.db import models
from django.conf import settings
#Model kun for arrangører av events

User = settings.AUTH_USER_MODEL

class OrganizerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organizer')
    organization_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.organization_name