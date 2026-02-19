''' 
Bidratt til denne filen:
    - Kamilla Nizamova
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import OrganizerProfile, UserProfile, Account

#django bestemmer selv hvilken user model som er i bruk
User = get_user_model()

class AccountCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name','last_name', 'email','phone_number', 'password1', 'password2')
        labels = {
            'first_name': 'Fornavn',
            'last_name': 'Etternavn',
            'email': 'E-post',
            'phone_number': 'Telefonnummer',
            'password1': 'Passord',
            'password2': 'Bekreft passord'
        }
       
        error_messages = {
        'first_name': {'required': "Fornavn er påkrevd."},
        'last_name': {'required': "Etternavn er påkrevd."},
        'email': {'invalid': "Skriv inn en gyldig e-postadresse."}
        }
    
    error_messages = {
    'password_mismatch': "Passordene må være like."
    }

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()

        if not email:
            raise forms.ValidationError("E-post er påkrevd.")

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
        labels = {
            'organization_name': 'Organisasjonsnavn',
            'contact_email': 'Kontakt e-post',
            'phone_number': 'Kontakt telefonnummer',
            'organization_number': 'Organisasjonsnummer'
        }



#forms for å redigere bruker profil 
#the first form will save data related to an account model
class UserForm(forms.ModelForm):
    class Meta:
        model = Account 
        fields = ('first_name', 'last_name', 'phone_number')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address', 'city', 'postal_code')
