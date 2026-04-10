# tickethub

## Arkivering av Arrangementer

Systemet har automatisk arkivering av avsluttede arrangementer (konserter og festivaler).

### Hvordan det fungerer

Når et arrangement er avsluttet (basert på `end_datetime`), kan det arkiveres til en separat tabell i databasen. Arrangementet markeres som arkivert (`is_archived=True`) og vil ikke lenger vises på offentlige sider, men ordrehistorikk og billettinformasjon bevares intakt.

### Kjøre arkivering manuelt

For å arkivere alle avsluttede arrangementer:

```bash
python3 manage.py archive_expired_events
```

For å arkivere arrangementer som ble avsluttet for minst 7 dager siden:

```bash
python3 manage.py archive_expired_events --days 7
```

### Hva arkiveres?

**I ArchivedEvent-tabellen lagres:**

- Alle arrangementdetaljer (tittel, beskrivelse, datoer)
- Artistinformasjon (kommaseparert liste)
- Venue og adresse (som tekst)
- Statistikk (antall solgte billetter, total inntekt)
- Bilder (stier lagres i ArchivedEventImage)

**Det opprinnelige Event-objektet:**

- Markeres som arkivert (`is_archived=True`)
- Beholdes i databasen for å bevare integritet med Orders og Tickets
- Vises ikke lenger på offentlige sider (home, all-events, festivals, etc.)

### Offentlige sider

Følgende sider er oppdatert til å ekskludere arkiverte arrangementer:

- Hjemmeside (`home_page`)
- Alle konserter (`all_events`)
- Festivaler (`festivals`)
- Byer (`cities`)
- Venue-detaljer (`venue_detail`)
- Venue-guide (`venue_guide`)

## REST API - Update event - JF og MB
Prosjektet inkluderer et REST API bygget med Django REST Framework for å håndtere arrangementer.
 
### Oppsett og kjøring
1. Installer avhengigheter:
   ```bash
   pip install -r requirements.txt
   ```

2. Kjør Django-serveren:
   ```bash
   python manage.py runserver
   ```

API-et vil være tilgjengelig på `http://localhost:8000/api/`.

### Endepunkter

#### Oppdater arrangement
- **URL:** `/api/events/{id}/`
- **Metode:** `PATCH` (delvis oppdatering) eller `PUT` (full oppdatering)
- **Beskrivelse:** Oppdaterer et eksisterende arrangement.

##### Eksempler på forespørsler

**PATCH - Delvis oppdatering:**
```bash
curl -X PATCH http://localhost:8000/api/events/1/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Oppdatert tittel"}'
```

**PUT - Full oppdatering:**
```bash
curl -X PUT http://localhost:8000/api/events/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "organizer": 1,
    "venue": 1,
    "title": "Nytt arrangement",
    "description": "Beskrivelse",
    "start_datetime": "2024-12-01T10:00:00Z",
    "end_datetime": "2024-12-01T12:00:00Z"
  }'
```

##### Svar

**Vellykket oppdatering (200 OK):**
```json
{
    "id": 1,
    "organizer": 1,
    "venue": 1,
    "title": "Oppdatert tittel",
    "description": "Beskrivelse",
    "performers": [],
    "event_type": "concert",
    "start_datetime": "2024-12-01T10:00:00Z",
    "end_datetime": "2024-12-01T12:00:00Z",
    "is_archived": false,
    "slug": "oppdatert-tittel"
}
```

##### Valideringsregler
- `title`: Påkrevd, maks 255 tegn
- `description`: Valgfri tekst
- `start_datetime`: Påkrevd, dato/klokkeslett i ISO-format
- `end_datetime`: Påkrevd, dato/klokkeslett i ISO-format (må være etter start_datetime)
- `organizer`: Påkrevd, ID for organizer
- `venue`: Påkrevd, ID for venue
- `event_type`: Valgfri, 'concert' eller 'festival'
- `performers`: Valgfri liste med performer-IDer

##### Feilkoder
- `400 Bad Request`: Ugyldig data (valideringsfeil)
- `404 Not Found`: Arrangementet finnes ikke
- `401 Unauthorized`: Ikke autentisert (hvis autentisering kreves)
- `403 Forbidden`: Ikke tillatelse til å oppdatere arrangementet

### Testing

Kjør enhetstester for API-et:
```bash
python manage.py test events.tests.EventAPITestCase
```


### Admin-panel

**Event Admin:**

- Viser `is_archived` i listen over arrangementer
- Filtrering etter arkiveringsstatus

**Archived Events Admin:**

- Skrivebeskyttet visning
- Kun superadmin kan slette
- Ingen manuell opprettelse tillatt

### Automatisk arkivering (anbefalt)

For å kjøre arkivering automatisk hver natt, legg til en cron-job eller scheduled task:

```bash
# Eksempel cron (kjør hver natt kl 03:00)
0 3 * * * cd /path/to/tickethub && python3 manage.py archive_expired_events
```

### Arkitektur

```
Event (aktiv) ---(arkiveres)---> Event (is_archived=True) + ArchivedEvent (kopi)
                                          |
                                          |-- Orders (bevares)
                                          |-- Tickets (bevares)
                                          |-- TicketTypes (bevares)
```

### Bidragsytere

- **Arkiveringssystem:** Nikita Pushechnikov
  - Modeller: ArchivedEvent, ArchivedEventImage
  - Management command: archive_expired_events
  - View-filtrering for arkiverte events
  - Admin-panelkonfiguration
