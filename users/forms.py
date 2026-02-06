''' 
Bidratt til denne filen:
    - Kamilla Nizamova
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import OrganizerProfile

#django bestemmer selv hvilken user model som er i bruk
User = get_user_model()

class AccountCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name','last_name', 'email','phone_number', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Denne e-posten er allerede i bruk.")
        return email


#sjekk om man er en vanlig bruker eller arrangør ved registrering
class SignupTypeForm(forms.Form):
     is_organizer = forms.BooleanField(required=False, label="Jeg er arrangør")


# form for å lage en arrangørprofil
class OrganizerProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizerProfile
        fields = ('organization_name', 'contact_email', 'phone_number', 'organization_number')