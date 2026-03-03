# TicketHub UI Style Guide (Team Rules)

Dette dokumentet er en praktisk regelbok for å holde visuell konsistens i hele prosjektet.

## 1) Scope og kildefiler

Reglene er basert på audit av alle CSS-filer i prosjektet:

- `static/main.css`
- `tickets/static/tickets/betaling.css`
- `tickets/static/tickets/after_payment.css`
- `users/static/users/login.css`
- `users/static/users/register.css`
- `users/static/users/user_profile.css`
- `users/static/users/my_orders.css`
- `users/static/users/organizer_profile.css`

## 2) Design Tokens (obligatorisk førstvalg)

Bruk alltid tokens fra `:root` i `static/main.css` før hardkodede farger.

### 2.1 Farger (kanoniske – aktiv palett)

Base:

- `--th-black`: `#000000` (app bakgrunn)
- `--th-dark-gray`: `#111111` (cards/sekundær bakgrunn)
- `--th-light-gray`: `#333333` (border/surface-kontrast)
- `--th-muted`: `#9ca3af` (sekundær tekst)
- `--th-white`: `#ffffff` (hovedtekst på mørk bakgrunn)
- `--th-red`: `#dc2626` (primær CTA/brand)
- `--th-red-dark`: `#b91c1c` (hover for primær CTA)
- `--th-green`: `#00c750` (success)
- `--th-info`: `#3b82f6` (info)

Alpha-tokens:

- `--th-black-a10`, `--th-black-a30`, `--th-black-a50`
- `--th-white-a04`
- `--th-red-a10`
- `--th-green-a08`
- `--th-info-a10`

### 2.2 Fargepolicy

1. Nye komponenter skal bruke `var(--th-...)`, ikke nye hex-koder.
2. Primær handling = `--th-red`, hover = `--th-red-dark`.
3. Sekundær tekst = `--th-muted`.
4. Default border på mørk bakgrunn = `--th-light-gray` eller `--th-white-a04`.
5. Ikke opprett nye “nesten like” varianter (f.eks. ekstra grå/rød-alpha) uten designbeslutning.

## 3) Legacy-farger (utfasing)

Farger utenfor aktiv palett kan fortsatt finnes i eldre komponenter.

Regel:

- Ikke bruk legacy hex/rgba i ny kode.
- Ved endring av eksisterende komponent: migrer mot aktiv palett i §2.1.

## 4) Typografi

### 4.1 Font family

- Global: `Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial`.

### 4.2 Anbefalt skala for nye UI-elementer

- Body-sm: `13px`
- Body: `14px`
- Body-lg: `16px`
- Label/meta: `12px`
- H6: `18px`
- H5/H4: `20–24px`
- Hero/display: bruk `clamp(...)` (som i `main.css`)

### 4.3 Verdier observert i prosjektet

`10px 11px 12px 13px 14px 15px 16px 18px 20px 24px`, og rem/em-varianter (`0.8rem` til `4rem`) samt flere `clamp(...)`.

Regel: Nye side-komponenter skal primært bruke `12/14/16/20/24px` eller tilsvarende rem.

## 5) Spacing

### 5.1 Basisskala (bruk denne konsekvent)

- `4px, 8px, 12px, 16px, 24px, 32px, 40px, 60px, 80px`

### 5.2 Komponentnivå

- Input-høyde/inner-padding: typisk `10–12px` vertikalt, `12–16px` horisontalt.
- Card padding: `24px` eller `32px`.
- Seksjonspadding: `60px` eller `80px` topp/bunn.

Regel: Unngå nye “mellomverdier” hvis nærmeste verdi i skala fungerer.

## 6) Radius

### 6.1 Radius i bruk

`4px, 5px, 6px, 8px, 10px, 12px, 16px, 20px, 0.5rem, 50%`

### 6.2 Standard for nye komponenter

- Inputs: `6px`
- Knapper: `8px`
- Cards/moduler: `12px`
- Pill/tag/små badges: `4px`
- Runde ikoner/avatarer: `50%`

## 7) Shadows

### 7.1 Standard shadows (anbefalt)

- Surface/card: `0 4px 16px rgba(0, 0, 0, 0.3)`
- Stor card/hero: `0 8px 32px rgba(0, 0, 0, 0.4)`
- Red CTA hover: `0 4px 12px rgba(220, 38, 38, 0.3)`
- Focus ring: `0 0 0 3px rgba(220, 38, 38, 0.1)`

Regel: Ikke innfør nye shadow-profiler uten behov.

## 8) Interaksjoner (hover/focus/active)

### 8.1 Hover-regler

- Primær knapp: bakgrunn fra `--th-red` til `--th-red-dark`.
- Cards: lett `transform` + shadow (ingen store hopp).
- Lenker i footer/nav: farge-overgang til rød eller hvit avhengig av kontrast.

### 8.2 Focus-regler

- Alle inputs/select/textarea må ha tydelig focus-state.
- Anbefalt: border i rød + svak ring.
- Ikke fjern focus-outline uten erstatning.

### 8.3 Transition-regler

Verdier observert: `0.2s`, `0.3s`, `0.4s` med `ease`.

Standard for nye komponenter:

- Farge/border/background: `0.2s ease`
- Transform/shadow: `0.2s ease`
- Store blokker/expansion: `0.3s ease`

## 9) Buttons

### 9.1 Primær knapp

- Background: `var(--th-red)`
- Text: `var(--th-white)`
- Radius: `8px`
- Hover: `var(--th-red-dark)`

### 9.2 Sekundær knapp

- Transparent bakgrunn
- Border: hvit eller `--th-light-gray`
- Hover: fyll/hardere kontrast

### 9.3 Disabled

- Lavere opacity + `cursor: not-allowed`
- Ingen hover-effekt som ser aktiv ut

## 10) Forms

### 10.1 Inputs

- Bakgrunn: `--th-dark-gray`
- Tekst: `--th-white`
- Border: `--th-light-gray`
- Radius: `6px`

### 10.2 Validation

- Error border/farge: `--th-red`
- Error-surface: `--th-red-a10`
- Success-surface: `--th-green-a08`

## 11) Cards og surfaces

- Standard card bg: `--th-dark-gray`
- Radius: `12px`
- Padding: `24–32px`
- Border: `--th-light-gray` eller `--th-white-a04`

## 12) Layout og responsivitet

### 12.1 Bredde

Observerte container-verdier inkluderer bl.a. `1100, 1200, 1280, 1300, 1400, 1500px`.

Teamregel for nye sider:

- Primær container: `max-width: 1280px`
- Smale content-sider: `max-width: 1100–1200px`

### 12.2 Breakpoints i bruk

- `min-width: 640px`, `min-width: 768px`
- `max-width: 400, 480, 576, 639, 768, 800, 950, 992, 1024, 1200px`

Teamregel:

- Primære breakpoints for nye komponenter: `640 / 768 / 1024 / 1200`.
- Ekstra breakpoint kun ved reelt layoutbehov.

## 13) Do / Don’t

### Do

- Bruk `--th-*` tokens først.
- Gjenbruk eksisterende komponentklasser/patterns der mulig.
- Hold deg til anbefalt spacing/radius/transition-skala.

### Don’t

- Ikke legg til nye tilfeldige hex-koder når token finnes.
- Ikke bland mange forskjellige radius/hover-stiler i samme view.
- Ikke bruk sterke animasjoner som bryter med dark/minimal uttrykk.

## 14) PR-checklist (må passere før merge)

1. Nye farger bruker tokens (`--th-*`) der mulig.
2. Knapper følger primær/sekundær-reglene.
3. Inputs har tydelig `:focus`.
4. Spacing følger basisskala.
5. Radius følger standard (`6/8/12px` som default).
6. Hover/focus er konsekvent med eksisterende mønster.
7. Responsivt testet på minst `<=768` og `>=1024`.

## 15) Neste anbefalte steg (for 100% konsistens)

1. Flytt legacy hardkodede farger gradvis til `--th-*` tokens.
2. Etabler en liten “component primitives” fil for felles button/input/card.
3. Legg til lint-regler/stylelint for å hindre nye tilfeldige farger.
