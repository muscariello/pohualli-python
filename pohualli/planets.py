from __future__ import annotations

# Full planetary logic port with friendly name mapping
P_MERCURY=1; P_VENUS=2; P_MARS=3; P_JUPITER=4; P_SATURN=5; P_URANUS=6; P_NEPTUNE=7; P_PLUTO=8

NAME_TO_INDEX = {
    'mercury': P_MERCURY,
    'venus': P_VENUS,
    'mars': P_MARS,
    'jupiter': P_JUPITER,
    'saturn': P_SATURN,
    'uranus': P_URANUS,
    'neptune': P_NEPTUNE,
    'pluto': P_PLUTO,
}

_PLANET_S = [None,115.9,583.92,779.9,398.88,378.09,369.7,367.5,366.7]
_CORR = [None,0,0.0000015,0,0,0,0,0,0]
_CORR_JDN = [None,0,2600000,0,0,0,0,0,0]
_PLANET_F1 = [None,76,176,-107,249,237,0,0,0]
_PLANET_F2 = [None,58,292,389,199,189,185,184,183]
_PLANET_F3 = [None,-58,-292,-390,-200,-189,-185,-184,-184]

def _get_correction(jdn: int, planet: int) -> float:
    return (_CORR_JDN[planet] - jdn) * _CORR[planet]

def julian_day_to_planet_synodic_val(jdn: int, planet: int | str) -> float:
    if isinstance(planet, str):
        planet = NAME_TO_INDEX[planet.lower()]
    period = _PLANET_S[planet]
    num = jdn / period
    n_int = int(num)
    val = jdn - (n_int * period)
    return val + _get_correction(jdn, planet)

def trunc_planet_synodic_val(syn_val: float, planet: int | str) -> int:
    if isinstance(planet, str):
        planet = NAME_TO_INDEX[planet.lower()]
    period = _PLANET_S[planet]
    syn_val = syn_val - (period / 2)
    number = round(syn_val)
    number += _PLANET_F1[planet]
    if number > _PLANET_F2[planet]:
        number = _PLANET_F3[planet] + (number - _PLANET_F2[planet])
    elif number < (_PLANET_F3[planet] + 1):
        number = _PLANET_F2[planet] - (_PLANET_F3[planet] - number)
    return number

def all_planets(jdn: int):
    out = {}
    for name in NAME_TO_INDEX:
        syn = julian_day_to_planet_synodic_val(jdn, name)
        out[name] = {
            'synodic_value': syn,
            'index': trunc_planet_synodic_val(syn, name)
        }
    return out
