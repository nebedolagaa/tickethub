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
