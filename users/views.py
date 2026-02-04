''' 
Bidratt til denne filen:
    - Kamilla Nizamova
'''
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.db import transaction

from .forms import AccountCreationForm, SignupTypeForm, OrganizerProfileForm

#funksjon for registrering av bruker
def register(request):
    if request.method == 'POST':
        user_form = AccountCreationForm(request.POST)
        type_form = SignupTypeForm(request.POST)

        type_valid = type_form.is_valid() #sjekk om type_form er gyldig før du prøver å hente data fra den
        is_organizer = type_valid and type_form.cleaned_data.get('is_organizer', False) # henter boolean fra checkbox (False hvis ikke huket av)

        organizer_form = OrganizerProfileForm(request.POST) if is_organizer else OrganizerProfileForm() #tom form hvis ikke arrangør

        ok = user_form.is_valid() and type_valid #brukerform og type_form må være gyldige for å fortsette
        if is_organizer:
            #legger inn en ny condition for ok
            ok = ok and organizer_form.is_valid() #hvis arrangør må også arrangørprofilen være gyldig

        if ok:
            with transaction.atomic(): #hvis noe går galt under opprettelsen av bruker eller arrangørprofil, vil ingen av dem bli opprettet
                user = user_form.save(commit=False)
                user.email = user.email.lower() #sørg for at e-posten alltid lagres i små bokstaver
                user.save()

                if is_organizer: 
                    organizer = organizer_form.save(commit=False)
                    organizer.user = user #knytt arrangørprofilen til user fordi arrangør er en rolle og ikke en egen user type 
                    organizer.save()

            login(request, user)
            return redirect('home_page') #omdiriger til hjemsiden etter registrering
        
    else:
        user_form = AccountCreationForm()
        type_form = SignupTypeForm()
        organizer_form = OrganizerProfileForm()

    #hvis det er en GET request eller hvis det er en POST request med ugyldige data, render registreringssiden med formene
    #(som vil vise valideringsfeil hvis det var en POST request)
    return render(request, 'users/register.html',
                  {'user_form': user_form,
                   'type_form': type_form,
                   'organizer_form': organizer_form})

