# Arkivering av arrangementer

Systemet arkiverer avsluttede arrangementer automatisk eller manuelt. Når et arrangement er avsluttet basert på `end_datetime`, kan det flyttes til arkivtabellene og merkes som arkivert med `is_archived=True`.

## Manuell arkivering

Arkiver alle avsluttede arrangementer:

```bash
python3 manage.py archive_expired_events
```

Arkiver bare arrangementer som ble avsluttet for minst 7 dager siden:

```bash
python3 manage.py archive_expired_events --days 7
```

## Hva som arkiveres

I arkivet lagres blant annet:

- Arrangementdetaljer som tittel, beskrivelse og datoer
- Artistinformasjon
- Venue og adresse
- Statistikk som antall solgte billetter og total inntekt
- Bilder via `ArchivedEventImage`

Originalobjektet beholdes i databasen for å bevare historikk og koblinger til ordre og billetter, men det skjules fra offentlige sider.

## Automatisk kjøring

For å kjøre arkivering hver natt kan du bruke en cron-jobb eller tilsvarende scheduled task:

```bash
0 3 * * * cd /path/to/tickethub && python3 manage.py archive_expired_events
```
