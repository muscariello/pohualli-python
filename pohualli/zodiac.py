# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from .types import ABSOLUTE

SAROS = 6585.32
STAR_YEAR = 365.25636574
EARTH_YEAR = 365.242199073
JD_STAR_ARIES_1995 = 2449827
JD_EARTH_ARIES_1995 = 2449798

_ZODIAC_NAMES = ['Ari','Tau','Gem','Cnc','Leo','Vir','Lib','Sco','Sgr','Cap','Aqr','Psc']

_DEF_NAME_MAP = {n.upper(): i for i,n in enumerate(_ZODIAC_NAMES)}

def zodiac_to_name(deg: int) -> str:
    if 0 <= deg < 360:
        return _ZODIAC_NAMES[deg // 30]
    return ''

def zodiac_name_to_index(name: str) -> int:
    up = name.strip().upper()
    # Implement Pascal-like initial char heuristics
    if not up:
        return 255
    ch = up[0]
    if ch == 'A':
        if len(up) > 1 and up[1] == 'R':
            return 0
        if len(up) > 1 and up[1] == 'Q':
            return 10
    elif ch == 'T':
        return 1
    elif ch == 'G':
        return 2
    elif ch == 'C':
        if len(up) > 2 and up[2] in ('N','C'):
            return 3
        if len(up) > 2 and up[2] == 'P':
            return 9
    elif ch == 'L':
        if len(up) > 1 and up[1] == 'E':
            return 4
        if len(up) > 1 and up[1] == 'I':
            return 6
    elif ch == 'V':
        return 5
    elif ch == 'S':
        if len(up) > 1 and up[1] == 'C':
            return 7
        if len(up) > 1 and up[1] in ('A','G'):
            return 8
    elif ch == 'P':
        return 11
    return 255

def zodiac_to_number(deg: int) -> int:
    if 0 <= deg < 360:
        nr = deg // 30
        return deg - (nr * 30)
    return 255

def sum_zodiacs(number: int, index: int) -> int:
    return (index * 30) + number

def _positional_angle(jdn: int, base_jdn: int, year_length: float) -> int:
    if jdn > base_jdn:
        delta = jdn - base_jdn
        nt = delta / year_length
        lt = int(nt)
        rem = delta - (lt * year_length)
        rem = (rem / year_length) * 360
        out = round(rem)
    else:
        delta = base_jdn - jdn
        nt = delta / year_length
        lt = int(nt)
        rem = delta - (lt * year_length)
        rem = year_length - rem
        rem = (rem / year_length) * 360
        out = round(rem)
    if out == 360:
        out = 0
    return out

def julian_day_to_star_zodiac(jdn: int) -> int:
    return _positional_angle(jdn, JD_STAR_ARIES_1995, STAR_YEAR)

def julian_day_to_earth_zodiac(jdn: int) -> int:
    return _positional_angle(jdn, JD_EARTH_ARIES_1995, EARTH_YEAR)
