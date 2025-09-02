from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple

LongCountDate = Tuple[int,int,int,int,int,int]

@dataclass
class TzolkinHaabCorrection:
    tzolkin: int = 0
    haab: int = 0
    g: int = 0
    lcd: int = 0

@dataclass
class SheetWindowConfig:
    tzolkin_haab_correction: TzolkinHaabCorrection = field(default_factory=TzolkinHaabCorrection)
    first_365_month: int = 0
    t_aztec: bool = False
    # Year bearer reference (analogous to SheetWindowRec.YearBearerStr/Val)
    year_bearer_str: int = 0  # Haab month index (0..18)
    year_bearer_val: int = 0  # Haab day number (0..19)
    # 819-cycle and direction/color corrections (extensions not in original Pascal struct name)
    cycle819_station_correction: int = 0
    cycle819_dir_color_correction: int = 0

# Global-like (kept configurable to avoid hidden state).
DEFAULT_CONFIG = SheetWindowConfig()

# Mutable correction record analog from Pascal (subset needed for Maya unit)
@dataclass
class CorrectionRecord:
    cTzolkinVal: int = 0
    cTzolkinStr: int = 0
    cGValue: int = 0
    cHaabVal: int = 0
    cLongCount: int = 0
    # Additional corrections (Pascal has more; placeholders)
    cWeekCorrection: int = 0

@dataclass
class AbsoluteCorrections:
    new_era: int = 584285
    abn_dist_first_day: int = 2009802
    maya_moon_first_day: int = 2002685
    julian_cycle_days: int = 1461
    gregorian_cycle_days: int = 146097
    julian_cycle_1_jan: int = 0
    gregorian_cycle_1_jan: int = -32104
    julian_first_year: int = -4713
    gregorian_first_year: int = -4801
    gregorian_correction_first_year: int = 1794168

ABSOLUTE = AbsoluteCorrections()

CORRECTIONS = CorrectionRecord()
