"""Correlation (Era / Absolute corrections) presets port.

Provides named sets of absolute correction constants similar to Pascal CorrectReset.
Only the core fields currently used by the Python port are applied; others are stored for future expansion.
"""
# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from dataclasses import dataclass
from .types import ABSOLUTE

@dataclass
class CorrelationPreset:
    name: str
    description: str
    new_era: int
    abn_dist_first_day: int = 2009802
    maya_moon_first_day: int = 2002685
    julian_cycle_days: int = 1461
    gregorian_cycle_days: int = 146097
    julian_cycle_first_jdn: int = 0
    gregorian_cycle_first_jdn: int = -32104
    julian_first_year: int = -4713
    gregorian_first_year: int = -4801
    gregorian_correction_first_jdn: int = 1794168


PRESETS: dict[str, CorrelationPreset] = {
    # Default from Settings.CorrectReset (New Era 584285)
    'default': CorrelationPreset(
        name='default',
        description='Default correlation (Goodman-Martinez-Thompson 584285)',
        new_era=584285,
    ),
    # Common scholarly alternate (584283) used in some datasets
    'gmt-584283': CorrelationPreset(
        name='gmt-584283',
        description='GMT variant 584283 (2 days earlier)',
        new_era=584283,
    ),
    # Spinden correlation (starting 489384) placeholder illustrative only
    'spinden': CorrelationPreset(
        name='spinden',
        description='Spinden (illustrative placeholder, verify before use)',
        new_era=489384,
    ),
}


def list_presets() -> list[CorrelationPreset]:
    return list(PRESETS.values())


_ACTIVE_PRESET: str | None = None

def apply_preset(name: str):
    global _ACTIVE_PRESET
    preset = PRESETS[name]
    ABSOLUTE.new_era = preset.new_era
    _ACTIVE_PRESET = name
    return preset

def active_preset_name() -> str | None:
    return _ACTIVE_PRESET
