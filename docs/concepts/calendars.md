# Calendars

Pohualli supports key Mesoamerican calendar cycles (see [Mesoamerican calendars](https://en.wikipedia.org/wiki/Mesoamerican_calendars)):

## Tzolk'in (260-day)
([Wikipedia](https://en.wikipedia.org/wiki/Tzolk%CA%BCin)) 13 numbers × 20 day names forming a 260‑day sacred cycle.

## Haab (365-day)
([Wikipedia](https://en.wikipedia.org/wiki/Haab%27)) 18 months × 20 days plus a 5‑day period (Uayeb / Nemontemi) for a 365‑day vague solar year.

## Long Count
([Wikipedia](https://en.wikipedia.org/wiki/Mesoamerican_Long_Count_calendar)) Linear day count using positional units: bak'tun, k'atun, tun, uinal, kin.

## 819-day Cycle
([Wikipedia – Maya calendar, 819‑day count](https://en.wikipedia.org/wiki/Maya_calendar#819-day_count)) A ritual / astronomical count attested in Classic Maya inscriptions. Each 819‑day span is associated with one of the four cardinal directions and colors (West Black, North White, East Red, South Yellow). In inscriptions the 819‑day period often appears alongside Long Count dates as a supplementary cycle.

### Structure
* Length: 819 days ( = 3 × 273 = 9 × 91 )
* Four stations (directional associations) give a 4 × 819 = 3276‑day directional cycle.
* Modern research (e.g. Saturno et al. 2023) notes that extending to 20×819 (= 16,380 days) yields alignments with multiple planetary synodic periods (Mercury, Venus, Mars, Jupiter, Saturn), suggesting a broader astronomical rationale beyond the earlier simpler 4‑station view.

### Directional Colors
| Station mod 4 | Direction | Color  | Spanish form (code) |
|---------------|-----------|--------|---------------------|
| 1             | West      | Black  | Oeste Negro         |
| 2             | North     | White  | Norte Blanco        |
| 3             | East      | Red    | Este Rojo           |
| 4             | South     | Yellow | Sur Amarillo        |

In the implementation (`cycle819.py`) the helper `julian_day_to_819_station(jdn, correction)` computes a 1‑based station number by:
```
station = floor((jdn - FIRST_JDN + correction) / 819) + 1   (for dates ≥ FIRST_JDN)
```
The intra‑cycle day (0–818) is `julian_day_to_819_value`, and `station_to_dir_col` maps the station to 1–4 (direction/color) applying an additional directional correction.

### Why 819?
Historic proposals tied 819 to multiples of 9 (lord of the night cycle) and 13 (fundamental ritual number) and to the 260‑day Tzolk'in (e.g. 819 ≡ 3 × 273, with 273 close to eclipses / half-year seasonal spans). Recent interpretations emphasize multi‑cycle planetary commensurability emerging over 4, 16 or 20 repetitions (see references below).

### Example
If `FIRST_JDN = 582642` and `jdn = 2451545` (J2000), with zero correction:
```
number = (2451545 - 582642) = 1868903
station = floor(1868903 / 819) + 1 = ... (large integer — only its mod 4 matters for direction)
color_index = station_to_dir_col(station, 0)  # 1..4
```

### References (819‑day discussion)
* Saturno, W. A., Stuart, D., Beliaev, D. (2023). Extended analysis of the 819‑day count and planetary synodic alignments. (Popular summaries referenced on Wikipedia).
* Bricker, V. & Bricker, H. (2011). *Astronomy in the Maya Codices.* (Context for supplementary series and cycles.)
* Tedlock, D. (1992). *Time and the Highland Maya.* (Broader calendrical background.)
* Aveni, A. (2001). *Skywatchers.* (General Mesoamerican archaeoastronomy.)


## Year Bearer
([Wikipedia – Maya calendar, Year Bearer](https://en.wikipedia.org/wiki/Maya_calendar#Year_Bearer)) The Haab position relative to a reference yields a Tzolk'in number + name that "bears" (names) the Haab year. Different regional traditions (e.g. Highland vs Lowland) vary which Haab days qualify and how they map to directional sets.

## References

- Mesoamerican calendars: https://en.wikipedia.org/wiki/Mesoamerican_calendars
- Tzolk'in: https://en.wikipedia.org/wiki/Tzolk%CA%BCin
- Haab': https://en.wikipedia.org/wiki/Haab%27
- Long Count: https://en.wikipedia.org/wiki/Mesoamerican_Long_Count_calendar
- 819-day count (specific Maya calendar section): https://en.wikipedia.org/wiki/Maya_calendar#819-day_count
- Year Bearer (specific Maya calendar section): https://en.wikipedia.org/wiki/Maya_calendar#Year_Bearer
 - Sołtysiak, Arkadiusz & Lebeuf, Arnold. (2011). Pohualli 1.01. A computer simulation of Mesoamerican calendar systems. 8(49), 165–168.
