from pohualli import (
    gregorian_correction_pascal, jdn_to_gregorian_pascal,
    jdn_to_gregorian, jdn_to_julian, weekday, DEFAULT_CONFIG, CORRECTIONS
)

# Basic parity checks with known JDN anchors.
# JDN 2451545 -> 2000-01-01 Gregorian, Saturday (ISO 6).

def test_weekday_with_correction():
    CORRECTIONS.cWeekCorrection = 0
    base = weekday(2451545)
    assert base == 6  # Saturday
    CORRECTIONS.cWeekCorrection = 1
    assert weekday(2451545) == 7
    CORRECTIONS.cWeekCorrection = 0


def test_pascal_gregorian_correction_sign():
    # Ensure correction function returns small integer around modern dates
    corr = gregorian_correction_pascal(2451545)
    # Expect within reasonable range (rough heuristic < 10000)
    assert abs(corr) < 10000


def test_pascal_gregorian_date_anchor():
    y,m,d = jdn_to_gregorian_pascal(2451545)
    assert (y,m,d) == (2000,1,1)


def test_gregorian_standard_vs_pascal():
    # For modern dates both algorithms should agree for baseline config
    y1,m1,d1 = jdn_to_gregorian(2451545)
    y2,m2,d2 = jdn_to_gregorian_pascal(2451545)
    assert (y1,m1,d1) == (y2,m2,d2)
