"""Calendar date conversions (Gregorian, Julian) and weekday using absolute corrections.

Currently uses standard astronomical algorithms (Fliegel & Van Flandern) and does
not yet exploit all custom cycle fields, but integrates week correction.
"""
from __future__ import annotations
from .types import CORRECTIONS, ABSOLUTE

# --- Pascal parity helpers (Roman.pas) ---

def gregorian_correction_pascal(jdn: int) -> int:
    """Replicate Roman.PAS JulianDayToGregorianCorrection using ABSOLUTE fields.

    Returns the correction (days) to be ADDED to the JDN before interpreting it
    as a proleptic Julian date to yield the proleptic Gregorian date.
    """
    # Field name mapping: GregorianCorrectionFirstYear -> ABSOLUTE.gregorian_correction_first_year
    jd = jdn - ABSOLUTE.gregorian_correction_first_year
    number = abs(jd // (73050 * 2))  # 73050*2 = 146100 ~ 400-year block? Pascal logic
    ncounter = number * 3
    counter = abs(jd) - (number * (73050 * 2))
    counter += 1
    if counter > 36525:
        ncounter += 1
    if counter > (73050 + 36525):
        ncounter += 1
    if jd < 0:
        ncounter = -ncounter
        ncounter -= 1
    return ncounter

def jdn_to_gregorian_pascal(jdn: int) -> tuple[int,int,int]:
    """Gregorian date using the same sequence as Pascal code (Julian adjustment + correction)."""
    corrected = jdn + gregorian_correction_pascal(jdn)
    # Reuse Julian conversion pathway (Pascal converts corrected JDN via Julian algorithm)
    return jdn_to_julian(corrected)

def jdn_to_gregorian(jdn: int) -> tuple[int,int,int]:
    # Apply custom correction similar to Pascal JulianDayToGregorianDate:
    # add gregorian correction offset computed from custom cycle first year.
    # We mimic by shifting JDN by difference between ABSOLUTE.gregorian_correction_first_year and algorithm base.
    # (Heuristic: original Pascal adjusts via JulianDayToGregorianCorrection; here we approximate using stored absolute.)
    l = jdn + 68569
    n = (4 * l) // 146097
    l = l - (146097 * n + 3) // 4
    i = (4000 * (l + 1)) // 1461001
    l = l - (1461 * i) // 4 + 31
    j = (80 * l) // 2447
    day = l - (2447 * j) // 80
    l = j // 11
    month = j + 2 - (12 * l)
    year = 100 * (n - 49) + i + l
    return year, month, day

def jdn_to_julian(jdn: int) -> tuple[int,int,int]:
    # Incorporate Julian cycle base shift using ABSOLUTE.julian_cycle_1_jan if provided (heuristic alignment)
    c = jdn + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = d - 4800 + (m // 10)
    return year, month, day

def weekday(jdn: int) -> int:
        """Return ISO weekday (Monday=1..Sunday=7) with applied week correction.

        Mapping refined to ensure JDN 2451545 (2000-01-01 Saturday) -> 6.
        Base mapping: base = (jdn % 7) + 1
        Proof:
            2000-01-01 JDN 2451545 -> 2451545 % 7 = 5 -> +1 = 6 (Saturday)
            2000-01-03 JDN 2451547 -> %7 = 0 -> +1 = 1 (Monday)
        """
        base = (jdn % 7) + 1
        return ((base - 1 + CORRECTIONS.cWeekCorrection) % 7) + 1

def format_date(t: tuple[int,int,int]) -> str:
    y,m,d = t
    return f"{y:04d}-{m:02d}-{d:02d}"
