from __future__ import annotations

# Constants from Planets.pas
P_MERCURY=1; P_VENUS=2; P_MARS=3; P_IUPITER=4; P_SATURN=5; P_URAN=6; P_NEPTUN=7; P_PLUTON=8
_PLANET_S = [None,115.9,583.92,779.9,398.88,378.09,369.7,367.5,366.7]
_CORR = [None,0,0.0000015,0,0,0,0,0,0]
_CORR_JDN = [None,0,2600000,0,0,0,0,0,0]
_PLANET_F = [
    None,
    (76,176,-107,249,237,0,0,0)[0:8],  # we will reconstruct below for clarity
]
# Reconstruct row-wise data exactly as Pascal (rows correspond to offsets)
_PLANET_F1 = [None,76,176,-107,249,237,0,0,0]
_PLANET_F2 = [None,58,292,389,199,189,185,184,183]
_PLANET_F3 = [None,-58,-292,-390,-200,-189,-185,-184,-184]


def _get_correction(jdn: int, planet: int) -> float:
    return (_CORR_JDN[planet] - jdn) * _CORR[planet]


def julian_day_to_planet_synodic_val(jdn: int, planet: int) -> float:
    period = _PLANET_S[planet]
    num = jdn / period
    n_int = int(num)
    val = jdn - (n_int * period)
    return val + _get_correction(jdn, planet)


def trunc_planet_synodic_val(syn_val: float, planet: int) -> int:
    period = _PLANET_S[planet]
    syn_val = syn_val - (period / 2)
    number = round(syn_val)
    number += _PLANET_F1[planet]
    if number > _PLANET_F2[planet]:
        number = _PLANET_F3[planet] + (number - _PLANET_F2[planet])
    elif number < (_PLANET_F3[planet] + 1):
        number = _PLANET_F2[planet] - (_PLANET_F3[planet] - number)
    return number
