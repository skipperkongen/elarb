# Strøm Arbitrage

> Datakilder: Henrik, Energi Data Service

Notebooks:
- [volatilitet](notebooks/volatilitet.ipynb)

Køb *kWh* billigt eller producer dem selv (e.g. med solceller). Gem dem på et batteri og sælg dem senere til en højere pris.

- [Aftagere](#Aftagere)
- [Forretnings modeller](#Forretnings-modeller)
- [Fysisk implementering](#Fysisk-implementering)
- [Datakilder](#Datakiler)
- [Analyser](#Analyser) (e.g. [flaskehalse](#Flaskehalse-i-transmissions-net), [sæsonvariation](#Sæsonvariation), volatilitet og forecasts)
- [Buy-sell policies](#Buy-sell-policies) (e.g. RL)
- [Intern dokumentation](#Intern-dokumentation)
- [Ekstern dokumentation](#Ekstern-dokumentation)

Optimeringsproblemer:
- Indkøb: maksimer afkast ved køb af assets
  - Hvilken balance mellem batterier og solceller?
  - Hvor skal man købe ejendomme?
- Styring: hvilken policy for at maksimere afkast af assets
  - hvornår skal man købe og sælge?

Analyser:
- ROI:
  - Hvad er ROI per kWh på batteri?
- Forecasts:
  - Hvad er min/max spotprisen på fremtidig dato
  - Hvad er spotprisen i fremtidig time/dato
- EDA:
  - Volatilitet, min/max spotpris per dag
- Netværk:
  - Visualisering af netværkskapacitet
  - Hvor meget kan man eksportere per lokalområde?

## Aftagere

- [Vindstød](https://www.vindstoed.dk/) - [sælg din strøm](https://www.vindstoed.dk/tilmelding-solcelle)
- [Nettopower](https://www.nettopower.dk/) - [sælg din strøm](https://www.nettopower.dk/el/saelg-din-stroem)
- [NRGi](https://nrgi.dk/) - [sælg din strøm](https://nrgi.dk/erhverv/vi-tilbyder/stroem/salg-af-solcellestroem/)


## Forretnings modeller


### Option 1: bliv registreret som forsyningsselskab.

Kort sagt:
- Man deltager i daglige auktioner, hvor man kan byde ind på at smide *x* kWh ind på nettet til pris *p*
- Spørgsmål: hvad sker der hvis man vinder buddet, men leverer x' < x kWh? Får man en bøde?
- Nettets behov fyldes op ved at acceptere de indkomne tilbud (billigste først)
- Prisen på den sidste “vinder” for at opfylde behovet afgør hvad alle får i betaling
- **Eksempel**: Nettet har et samlet behov på 101 megawatt og der er to udbydere, *A* og *B*. Udbyder *A* byder ind med 100 megawatt til 1 kr/kWh. Udbyder *B* byder ind med 1 megawatt til 50 kr/kWh. Nettet bliver nødt til at acceptere begge tilbud for at nå op på 101 kWh. Både udbyder *A* og *B* får 50 kr/kWh. Det er derfor priserne er eksploderet
- Det er marginal-prisen der afgør gennemsnitsprisen og marginalen i Danmark er gas (og lidt markedsmanipulation..)

Fordele:
- TODO

Ulemper:
- TODO

### Option 2: Det “nemme” hack

Kort sagt:
- Som privat må du p.t. smide et 50 kW solcelle anlæg op uden problemer
- Man skal derefter have et forsyningsnummer
- Med det forsyningsnummer må du fylde strøm ind på nettet. Der står ikke noget om det “kun” må være fra dine solceller.
- Strøm afregnes til *spotpris* minus *moms* og *afgifter*

Fordele:
- TODO

Ulemper:
- TODO

Spørgsmål:
- Ingen spørgsmål

## Fysisk implementering

### Implementering 1: skibscontaineren

Kort sagt:
- Skibscontainer som enhed for både produktion, akkumulering og forbindelse.
- Solceller på taget (produktion) og batterier på indersiden (akkumulering).
- Understøtter både ren produktion og arbitrage
-

Fordele:
- Nem at flytte hvilket giver to fordele
  - God brandsikkerhed
  - Balancer placering ift flaskehalse

Ulemper:
- TODO

Spørgsmål:
- Hvor skal de stå?
- Skal man eje det land de står på?
- Hvordan flytter man dem?
- Praktisk: hvad er opskriften på at bygge dem?


### Implementering 2: rønnen

TODO

## Datakilder

[Energi Data Service](https://www.energidataservice.dk/):
- [API guide](https://www.energidataservice.dk/guides/api-guides)
- [Datasets](https://www.energidataservice.dk/datasets)

[Electricity maps](https://github.com/electricitymaps/electricitymaps-contrib)
- [Web app](https://app.electricitymaps.com/map)
- [Data](???)

[Kaj Munk Wen](https://wen.dk/):
- [Rå spot-priser denne uge (minus moms/afgift)](https://elpris2.wen.dk/)


## Analyser

### Flaskehalse i transmissions-net

Strøm skal transporteres fra udbyder til aftager gennem transmissions-netværket. På grund af netværkseffekter, kan der nemt opstå flaskehalse, hvilket begrænser hvor meget der kan leveres på tværs af geografiske områder. Derfor er det måske bedre at have mange små enheder fordelt geografisk.

### Sæsonvariation

TODO: FFT, sinus-cosinus etc. Hvor kan man få historiske data? EDS?

### Volatilitet

https://elpris2.wen.dk/


## Buy-sell policies

## Intern dokumentation

## Ekstern dokumentation

LifePo4 batterier:
- Køb i Kina
- Giver 2377 kr / kWh effektivt
- Forventer at kunne vride 8000 cycles ud med god temperatur styring.
- Dvs. en rå kostpris på 30 øre for at gemme en kWh
- Læg dertil konverterings-tab på 7-8% ved op/ned ladning
