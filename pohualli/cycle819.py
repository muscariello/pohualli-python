# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from .types import CORRECTIONS

FIRST_JDN = 582642
CYCLE_LONGITUDE = 819

def julian_day_to_819_station(jdn: int, correction: int) -> int:
    number = (jdn - FIRST_JDN) + correction
    number //= CYCLE_LONGITUDE
    if jdn >= FIRST_JDN:
        number += 1
    return number


def julian_day_to_819_value(jdn: int, correction: int) -> int:
    station = julian_day_to_819_station(jdn, correction)
    temp = (jdn - FIRST_JDN) + correction
    temp = temp - (CYCLE_LONGITUDE * (station - 1))
    if temp > 819:
        temp -= (temp // 819) * 819
    return temp


def station_to_dir_col(station: int, correction: int) -> int:
    station = station + correction
    if station < 0:
        station -= 3
        number = station // 4
        number = station - (number * 4)
        return number + 4
    number = station // 4
    number = station - (number * 4)
    return number + 1

_DIR_COL_STR = {
    1: 'Oeste Negro',
    2: 'Norte Blanco',
    3: 'Este Rojo',
    4: 'Sur Amarillo'
}

import unicodedata

def _normalize(s: str) -> str:
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).upper()

_DIR_COL_LOOKUP = { _normalize(v): k for k,v in _DIR_COL_STR.items() }


def dir_col_str_to_val(s: str) -> int:
    s = _normalize(s)
    # approximate matching like Pascal case distinctions
    for k,v in _DIR_COL_LOOKUP.items():
        if k.startswith(s) or s.startswith(k):
            return v
    return 255


def dir_col_val_to_str(v: int) -> str:
    return _DIR_COL_STR.get(v, '')
