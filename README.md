# Radar makro — historia

Dzienne zrzuty zakładki **Radar** z dashboardu *Puls Finansów*: cztery sygnały ostrzegawcze, kontekst rynkowy i najważniejsze wiadomości ze świata. Repo zasila codzienne zadanie (ok. 6:52 czasu polskiego) — jeden commit na dzień.

Zawiera wyłącznie dane rynkowe i wiadomości. Żadnych kwot z portfela ani wydatków.

## Pliki

| Plik | Co zawiera |
|---|---|
| `dni/RRRR-MM-DD.json` | pełny zrzut radaru z danego dnia (ten sam format co na dashboardzie) |
| `sygnaly.csv` | jeden wiersz na dzień: wartości, daty i stany czterech sygnałów + kontekst (Fed, 10-latki USA, BTC, złoto, NBP) i liczba alarmów |
| `wiadomosci.csv` | jedna linia na wiadomość; `pierwszy_raz` / `ostatni_raz` / `dni_na_radarze` pokazują, jak długo temat był ważny |
| `narzedzia/dopisz.py` | dopisuje zrzut dnia i przebudowuje oba pliki CSV ze wszystkich `dni/*.json` |

## Sygnały i progi alarmu

| Klucz | Sygnał | Próg alarmu |
|---|---|---|
| `hy` | spread obligacji wysokiego ryzyka (ICE BofA US HY OAS) | > 4,0 pp |
| `krzywa` | rentowność 10 lat minus 2 lata (USA) | +0,5 pp w 3 mies. przy spadających 2-latkach |
| `bezrobocie` | stopa bezrobocia w USA (BLS) | ≥ 4,6% |
| `brent` | ropa Brent | > 120 USD |

Stany: `ok`, `watch` (do obserwacji), `alarm`. Alarm radaru = 2 z 4 sygnałów naraz.

## Ręczne dopisanie dnia

```
python3 narzedzia/dopisz.py radar.json          # dzień z pola "updated"
python3 narzedzia/dopisz.py radar.json 2026-09-28
```

Analiza informacyjna — nie jest poradą inwestycyjną.
