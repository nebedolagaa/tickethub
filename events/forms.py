"""
Bidratt til denne filen:
    - Nikita Pushechnikov
"""
from django import forms
from .models import Event, Performer, Venue, VenueArea
from tickets.models import TicketType


class EventForm(forms.ModelForm):
    performers = forms.ModelMultipleChoiceField(
        queryset=Performer.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Artister / utøvere",
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "event_type",
            "venue",
            "start_datetime",
            "end_datetime",
            "performers",
        ]
        labels = {
            "title": "Tittel",
            "description": "Beskrivelse",
            "event_type": "Type arrangement",
            "venue": "Lokasjon",
            "start_datetime": "Startdato og tid",
            "end_datetime": "Sluttdato og tid",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "NP-input", "placeholder": "Navn på arrangementet"}),
            "description": forms.Textarea(attrs={"class": "NP-input NP-textarea", "rows": 4, "placeholder": "Beskrivelse av arrangementet"}),
            "event_type": forms.Select(attrs={"class": "NP-select"}),
            "venue": forms.Select(attrs={"class": "NP-select", "id": "id_venue"}),
            "start_datetime": forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"class": "NP-input", "type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"class": "NP-input", "type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["venue"].required = False

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_datetime")
        end = cleaned_data.get("end_datetime")
        if start and end and end <= start:
            raise forms.ValidationError("Sluttidspunkt må være etter starttidspunkt.")
        return cleaned_data


class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = ["name", "venue_area", "price", "quantity"]
        labels = {
            "name": "Billettype",
            "venue_area": "Sone",
            "price": "Pris (kr)",
            "quantity": "Antall billetter",
        }
        widgets = {
            "name": forms.Select(attrs={"class": "NP-select"}),
            "venue_area": forms.Select(attrs={"class": "NP-select", "id": "id_venue_area"}),
            "price": forms.NumberInput(attrs={"class": "NP-input", "min": "0", "step": "0.01", "placeholder": "0.00"}),
            "quantity": forms.NumberInput(attrs={"class": "NP-input", "min": "1", "placeholder": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["venue_area"].required = False
