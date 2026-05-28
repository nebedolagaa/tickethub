''' 
Bidratt til denne filen:
    - Kamilla Nizamova
'''
from django import forms
import re
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

        widgets = {
            'phone_number': forms.TextInput(attrs={
                'type': 'tel',
                'maxlength': '15',
                'inputmode': 'tel',
                'pattern': r'[\+\d\s\-]{7,15}',
                'placeholder': '+47 123 45 678',
            }),
        }
        error_messages = {
            'first_name': {'required': "Fornavn er påkrevd."},
            'last_name': {'required': "Etternavn er påkrevd."},
            'email': {'invalid': "Skriv inn en gyldig e-postadresse."},
        }

    error_messages = {
        'password_mismatch': "Passordene må være like.",
    }

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()

        if not email:
            raise forms.ValidationError("E-post er påkrevd.")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Denne e-posten er allerede i bruk.")

        return email

    def clean_first_name(self):
        name = (self.cleaned_data.get('first_name') or '').strip()
        if not name:
            raise forms.ValidationError("Fornavn er påkrevd.")
        if not re.match(r'^[A-Za-zÆØÅæøå\s\-]+$', name):
            raise forms.ValidationError("Fornavn kan kun inneholde bokstaver, mellomrom og bindestrek.")
        return name

    def clean_last_name(self):
        name = (self.cleaned_data.get('last_name') or '').strip()
        if not name:
            raise forms.ValidationError("Etternavn er påkrevd.")
        if not re.match(r'^[A-Za-zÆØÅæøå\s\-]+$', name):
            raise forms.ValidationError("Etternavn kan kun inneholde bokstaver, mellomrom og bindestrek.")
        return name

    def clean_phone_number(self):
        phone = (self.cleaned_data.get('phone_number') or '').strip()
        if phone and not re.match(r'^\+?[\d\s\-]{7,15}$', phone):
            raise forms.ValidationError("Skriv inn et gyldig telefonnummer (7–15 sifre).")
        return phone


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
        fields = ('first_name', 'last_name', 'email', 'phone_number')

        widgets = {
            'phone_number': forms.TextInput(attrs={
                'type': 'tel',
                'maxlength': '15',
                'inputmode': 'tel',
                'pattern': r'[\+\d\s\-]{7,15}',
                'placeholder': 'Ikke registrert',
                'class': 'form-control',
            }),
        }

    def clean_first_name(self):
        name = (self.cleaned_data.get('first_name') or '').strip()
        if not name:
            raise forms.ValidationError("Fornavn er påkrevd.")
        if not re.match(r'^[A-Za-zÆØÅæøå\s\-]+$', name):
            raise forms.ValidationError("Fornavn kan kun inneholde bokstaver, mellomrom og bindestrek.")
        return name

    def clean_last_name(self):
        name = (self.cleaned_data.get('last_name') or '').strip()
        if not name:
            raise forms.ValidationError("Etternavn er påkrevd.")
        if not re.match(r'^[A-Za-zÆØÅæøå\s\-]+$', name):
            raise forms.ValidationError("Etternavn kan kun inneholde bokstaver, mellomrom og bindestrek.")
        return name

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            raise forms.ValidationError("E-post er påkrevd.")
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Denne e-posten er allerede i bruk.")
        return email

    def clean_phone_number(self):
        phone = (self.cleaned_data.get('phone_number') or '').strip()
        if phone and not re.match(r'^\+?[\d\s\-]{7,15}$', phone):
            raise forms.ValidationError("Skriv inn et gyldig telefonnummer (7–15 sifre).")
        return phone


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address', 'city', 'postal_code')

        widgets = {
            'address': forms.TextInput(attrs={
                'placeholder': 'Ikke registrert',
                'class': 'form-control'
        }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Ikke registrert',
                'class': 'form-control'
        }),
            'postal_code': forms.TextInput(attrs={
                'placeholder': 'Ikke registrert',
                'maxlength': '4',
                'inputmode': 'numeric',
                'pattern': r'\d{4}',
                'class': 'form-control',
        }),
        }

    def clean_postal_code(self):
        code = (self.cleaned_data.get('postal_code') or '').strip()
        if code and not re.match(r'^\d{4}$', code):
            raise forms.ValidationError("Postnummer må bestå av 4 sifre.")
        return code

    def clean_city(self):
        city = (self.cleaned_data.get('city') or '').strip()
        if city and not re.match(r'^[A-Za-zÆØÅæøå\s\-]+$', city):
            raise forms.ValidationError("By kan kun inneholde bokstaver, mellomrom og bindestrek.")
        return city


class OrganizerProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizerProfile
        fields = ('organization_name', 'contact_email', 'phone_number', 'organization_number', 'organization_address', 'organization_city', 'organization_postcode')

        widgets = {
            'organization_name': forms.TextInput(attrs={
                'placeholder': 'Ikke registrert',
                'class': 'form-control',
            }),
            'organization_number': forms.TextInput(attrs={
                'placeholder': 'Ikke registrert',
                'class': 'form-control',
            }),
            'organization_address': forms.TextInput(attrs={
                'placeholder': 'Ikke registrert',
                'class': 'form-control',
            }),
            'organization_city': forms.TextInput(attrs={
                'placeholder': 'Ikke registrert',
                'class': 'form-control',
            }),
            'organization_postcode': forms.TextInput(attrs={
                'placeholder': 'Ikke registrert',
                'maxlength': '4',
                'inputmode': 'numeric',
                'pattern': r'\d{4}',
                'class': 'form-control',
            }),
        }

    def clean_organization_name(self):
        name = (self.cleaned_data.get('organization_name') or '').strip()
        if not name:
            raise forms.ValidationError("Organisasjonsnavn er påkrevd.")
        if len(name) < 2:
            raise forms.ValidationError("Organisasjonsnavn må ha minst 2 tegn.")
        return name

    def clean_organization_number(self):
        org_num = (self.cleaned_data.get('organization_number') or '').strip()
        if org_num and not re.match(r'^\d{9}$', org_num):
            raise forms.ValidationError("Organisasjonsnummeret må bestå av nøyaktig 9 sifre.")
        return org_num

    def clean_phone_number(self):
        phone = (self.cleaned_data.get('phone_number') or '').strip()
        if phone and not re.match(r'^\+?[\d\s\-]{7,15}$', phone):
            raise forms.ValidationError("Skriv inn et gyldig telefonnummer (7–15 sifre).")
        return phone

    def clean_organization_postcode(self):
        code = (self.cleaned_data.get('organization_postcode') or '').strip()
        if code and not re.match(r'^\d{4}$', code):
            raise forms.ValidationError("Postnummer må bestå av 4 sifre.")
        return code

    def clean_organization_city(self):
        city = (self.cleaned_data.get('organization_city') or '').strip()
        if city and not re.match(r'^[A-Za-zÆØÅæøå\s\-]+$', city):
            raise forms.ValidationError("By kan kun inneholde bokstaver, mellomrom og bindestrek.")
        return city
