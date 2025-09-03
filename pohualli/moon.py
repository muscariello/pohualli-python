# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from .types import ABSOLUTE

SIDERIC_MOON = 27.123832
SYNODIC_MOON = 29.207338
MAYA_MOON = 29.530588
DRAGON_MOON = 27.2122
ANOMALISTIC_MOON = 27.5546
ABN_DIST = 173.31

# Pascal uses Frac; replicate with value - int(value)

def _frac(x: float) -> float:
    return x - int(x)

def julian_day_to_maya_moon(jdn: int) -> float:
    if jdn < ABSOLUTE.maya_moon_first_day:
        number = _frac((ABSOLUTE.maya_moon_first_day - jdn) / MAYA_MOON)
        return MAYA_MOON - (number * MAYA_MOON)
    number = _frac((jdn - ABSOLUTE.maya_moon_first_day) / MAYA_MOON)
    return number * MAYA_MOON

def str_maya_moon(value: float) -> int:
    v = round(value)
    return 30 if v == 0 else v

def julian_day_to_abn_dist(jdn: int) -> float:
    if jdn < ABSOLUTE.abn_dist_first_day:
        number = _frac((ABSOLUTE.abn_dist_first_day - jdn) / ABN_DIST)
        number = ABN_DIST - (number * ABN_DIST)
    else:
        number = _frac((jdn - ABSOLUTE.abn_dist_first_day) / ABN_DIST)
        number = number * ABN_DIST
    if number > 86.655:
        number -= ABN_DIST
    return number

def str_abn_dist(val: float) -> int:
    return round(val)

def ecliptic(maya_moon_val: float, abn_dist_val: float) -> bool:
    return ((maya_moon_val < 1) or (maya_moon_val > 28.53)) and (abs(abn_dist_val) < 15)
