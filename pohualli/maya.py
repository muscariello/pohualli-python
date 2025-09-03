# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from .types import DEFAULT_CONFIG, CORRECTIONS, LongCountDate, ABSOLUTE
from .aztec import number_to_aztec_tzolkin_name, number_to_aztec_haab_name

# Constants from Pascal (Era length fixed; New Era offset configurable)
ERA_LENGTH = 1872000


_TZOLKIN_TABLE = [
 'Ahau','Imix','Ik','Akbal','Kan','Chicchan','Cimi','Manik','Lamat',
 'Muluc','Oc','Chuen','Eb','Ben','Ix','Men','Cib','Caban','Etznab','Cauac'
]

_HAAB_TABLE = [
 'Pop','Uo','Zip','Zotz','Tzec','Xul','Yaxkin','Mol','Ch\'en','Yax','Zac',
 'Ceh','Mac','Kankin','Muan','Pax','Kayab','Cumhu','Uayeb'
]

# --- Name / number conversions ---

def tzolkin_number_to_name(number: int) -> str:
    if DEFAULT_CONFIG.t_aztec:
        return number_to_aztec_tzolkin_name(number) if 0 <= number < 20 else ''
    return _TZOLKIN_TABLE[number] if 0 <= number < 20 else ''


def tzolkin_name_to_number(name: str) -> int:
    name_u = name.strip().upper()
    for i in range(20):
        if tzolkin_number_to_name(i).upper() == name_u:
            return i
    return 255


def haab_number_to_name(number: int) -> str:
    if number < 18:
        number = (number + DEFAULT_CONFIG.first_365_month) % 18
    if DEFAULT_CONFIG.t_aztec:
        return number_to_aztec_haab_name(number) if 0 <= number < 19 else ''
    return _HAAB_TABLE[number] if 0 <= number < 19 else ''


def haab_number_to_name2(number: int) -> str:
    if DEFAULT_CONFIG.t_aztec:
        return number_to_aztec_haab_name(number) if 0 <= number < 19 else ''
    return _HAAB_TABLE[number] if 0 <= number < 19 else ''


def haab_name_to_number(name: str) -> int:
    name_u = name.strip().upper()
    for i in range(19):
        if haab_number_to_name(i).upper() == name_u:
            return i
    return 255

# --- Julian Day conversions ---

# Follows Pascal logic; large multipliers kept to preserve period wrap-around.

def julian_day_to_tzolkin_value(day: int) -> int:
    day = day + DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin + 2
    day = day + CORRECTIONS.cTzolkinVal
    if day < 0:
        day += (165191049 * 13)
    day_mod = ((day % 13) + 13) % 13
    day_mod = day_mod + 4
    if day_mod > 13:
        day_mod -= 13
    return day_mod


def julian_day_to_tzolkin_name_index(day: int) -> int:
    day = day + DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin + 2
    day = day + CORRECTIONS.cTzolkinStr
    if day < 0:
        day += (107374182 * 20)
    day_mod = ((day % 20) + 20) % 20
    day_mod = day_mod + 15
    if day_mod >= 20:
        day_mod -= 20
    return day_mod


def julian_day_to_g_value(day: int) -> int:
    day = day + DEFAULT_CONFIG.tzolkin_haab_correction.g + 2
    day = day + CORRECTIONS.cGValue
    if day < 0:
        day += (238609294 * 9)
    day_mod = ((day % 9) + 9) % 9
    day_mod = day_mod + 4
    if day_mod > 9:
        day_mod -= 9
    return day_mod


def julian_day_to_haab_packed(day: int) -> int:
    day = day + DEFAULT_CONFIG.tzolkin_haab_correction.haab + 2
    day = day + CORRECTIONS.cHaabVal
    if day >= 0:
        day_mod = day % 365
        day_mod = day_mod + 63
        if day_mod >= 365:
            day_mod -= 365
    else:
        day_abs = -day
        day_mod = day_abs % 365
        day_mod = 365 - (day_mod - 63)
        if day_mod >= 365:
            day_mod -= 365
    return day_mod


def unpack_haab_value(value: int) -> int:
    return value % 20


def unpack_haab_month(value: int) -> int:
    return value // 20


def julian_day_to_long_count(day: int) -> LongCountDate:
    day = day + DEFAULT_CONFIG.tzolkin_haab_correction.lcd + 2
    day = day + CORRECTIONS.cLongCount
    counter = False
    new_era = ABSOLUTE.new_era
    if day < (new_era - ERA_LENGTH):
        counter = True
        day += (1145 * ERA_LENGTH)
    day = day + (ERA_LENGTH - new_era)
    out = []
    # bak'tun: 13*20*20*18*20
    mult = 13 * 20 * 20 * 18 * 20
    b = day // mult
    out.append(b)
    day -= b * mult
    mult = 20 * 20 * 18 * 20
    k = day // mult
    out.append(k)
    day -= k * mult
    mult = 20 * 18 * 20
    t = day // mult
    out.append(t)
    day -= t * mult
    mult = 18 * 20
    u = day // mult
    out.append(u)
    day -= u * mult
    mult = 20
    v = day // mult
    out.append(v)
    w = day - v * mult
    out.append(w)
    if counter:
        out[0] -= 1145
    return tuple(out)  # type: ignore


def long_count_to_julian_day(lc: LongCountDate) -> int:
    b,k,t,u,v,w = lc
    num = 0
    num += b * 13 * 20 * 20 * 18 * 20
    num += k * 20 * 20 * 18 * 20
    num += t * 20 * 18 * 20
    num += u * 18 * 20
    num += v * 20
    num += w
    new_era = ABSOLUTE.new_era
    return num - ((ERA_LENGTH - new_era) + CORRECTIONS.cLongCount + DEFAULT_CONFIG.tzolkin_haab_correction.lcd + 2)
