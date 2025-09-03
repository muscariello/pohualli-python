# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from .types import DEFAULT_CONFIG

# Direct tables derived from Pascal Aztec unit
_AZTEC_TZOLKIN_NAMES = [
 'Xochitl','Cipactli','Ehecatl','Calli','Ceutzpallin','Coatl',
 'Miquiztli','Mazatl','Tochtli','Atl','Itzcuintli','Ozomatli',
 'Malinalli','Acatl','Ocelotl','Cuauhtli','Cozcacuauhtli','Ollin',
 'Tecpatl','Quiahuitl'
]

_AZTEC_HAAB_NAMES = [
 'Atlcahualo','Tlacaxipehualitzli','Tezoztontli','Huey Tozoztli','Toxcatl','Etzalcualiztli','Tecuilhuitontli',
 'Huey Tecuilhuitl','Tlaxochimaco','Xocotl Huetzi','Ochpanitztli','Teotleco','Tepeilhuitl','Quecholli','Panquetzaliztli',
 'Atemoztli','Tititl','Izcalli','Nemontemi'
]

# Mapping heuristics copied from Pascal case distinctions.
# For clarity we implement straightforward dictionary lookup after normalization.
import unicodedata

def _normalize(name: str) -> str:
    name = name.strip()
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(ch for ch in name if not unicodedata.combining(ch))
    return name.upper()

_AZTEC_TZOLKIN_INDEX = { _normalize(n): i for i,n in enumerate(_AZTEC_TZOLKIN_NAMES) }
_AZTEC_HAAB_INDEX = { _normalize(n): i for i,n in enumerate(_AZTEC_HAAB_NAMES) }


def aztec_tzolkin_name_to_number(name: str) -> int:
    return _AZTEC_TZOLKIN_INDEX.get(_normalize(name), 255)


def number_to_aztec_tzolkin_name(number: int) -> str:
    return _AZTEC_TZOLKIN_NAMES[number]


def aztec_haab_name_to_number(name: str) -> int:
    return _AZTEC_HAAB_INDEX.get(_normalize(name), 255)


def number_to_aztec_haab_name(number: int) -> str:
    return _AZTEC_HAAB_NAMES[number]
