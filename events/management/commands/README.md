# tickethub

## Arkivering av Arrangementer

Systemet har automatisk arkivering av avsluttede arrangementer (konserter og festivaler).

### Hvordan det fungerer

Når et arrangement er avsluttet (basert på `end_datetime`), kan det arkiveres til en separat tabell i databasen. Dette holder databasen ren og optimalisert, samtidig som historiske data bevares.

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

- Alle arrangementdetaljer
- Artistinformasjon
- Venue og adresse
- Statistikk (antall solgte billetter, total inntekt)
- Bilder (stier lagres)

### Admin-panel

Arkiverte arrangementer kan sees i Django Admin under "Archived Events". De er skrivebeskyttet og kan bare slettes av superadmin.

### Bidragsytere

- Arkiveringssystem: Nikita Pushechnikov
