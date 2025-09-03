"""Auto-correction derivation (subset of Pascal AUTOCORR.PAS).

Given a target JDN and textual representations of calendar positions, brute-force
the minimal correction offsets for tzolkin (0..259), haab (0..364), 9-day cycle (0..8),
and long count (lcd) so that the internally computed values match the provided ones.

Year bearer reference (haab month/day) may also be derived from a supplied year bearer
string like "9 Ix" (number + tzolkin name) using a brute force search of 19*20 combos.

This intentionally ignores 819 and direction-color corrections for now.
"""
# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .maya import (
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index,
    tzolkin_number_to_name, julian_day_to_haab_packed, unpack_haab_month,
    unpack_haab_value, haab_number_to_name, julian_day_to_g_value,
    julian_day_to_long_count
)
from .yearbear import year_bearer_packed, unpack_yb_str, unpack_yb_val
from .types import TzolkinHaabCorrection, SheetWindowConfig
from .cycle819 import julian_day_to_819_station, julian_day_to_819_value, station_to_dir_col


@dataclass
class AutoCorrectionResult:
    tzolkin_offset: int
    haab_offset: int
    g_offset: int
    lcd_offset: int
    year_bearer_month: Optional[int]
    year_bearer_day: Optional[int]
    cycle819_station_correction: Optional[int] = None
    cycle819_dir_color_correction: Optional[int] = None

def _parse_tzolkin(spec: str) -> tuple[int,int]:
    parts = spec.strip().split()
    if len(parts) != 2:
        raise ValueError('Tzolkin spec must be "<value> <name>"')
    val = int(parts[0])
    name_upper = parts[1].upper()
    # find name index
    for i in range(20):
        if tzolkin_number_to_name(i).upper() == name_upper:
            return val, i
    raise ValueError('Unknown tzolkin name')

def _parse_haab(spec: str) -> tuple[int,int]:
    parts = spec.strip().split()
    if len(parts) != 2:
        raise ValueError('Haab spec must be "<day> <month>"')
    day = int(parts[0])
    name_upper = parts[1].upper()
    for i in range(19):
        if haab_number_to_name(i).upper() == name_upper:
            return day, i
    raise ValueError('Unknown haab month')

def _parse_year_bearer(spec: str) -> tuple[int,int]:
    parts = spec.strip().split()
    if len(parts) != 2:
        raise ValueError('Year bearer spec must be "<value> <tzolkin_name>"')
    val = int(parts[0])
    name_upper = parts[1].upper()
    for i in range(20):
        if tzolkin_number_to_name(i).upper() == name_upper:
            return val, i
    raise ValueError('Unknown tzolkin name in year bearer')

def derive_auto_corrections(
    jdn: int,
    *,
    tzolkin: str | None = None,
    haab: str | None = None,
    g_value: int | None = None,
    long_count: str | None = None,
    year_bearer: str | None = None,
    cycle819_station: int | None = None,
    cycle819_value: int | None = None,
    dir_color: str | None = None,
    base_config: SheetWindowConfig | None = None,
) -> AutoCorrectionResult:
    cfg = base_config or SheetWindowConfig()
    # We work on a local copy of correction fields
    tz_offset = cfg.tzolkin_haab_correction.tzolkin
    haab_offset = cfg.tzolkin_haab_correction.haab
    g_offset = cfg.tzolkin_haab_correction.g
    lcd_offset = cfg.tzolkin_haab_correction.lcd
    c819_station_corr = cfg.cycle819_station_correction
    c819_dir_col_corr = cfg.cycle819_dir_color_correction

    # Tzolkin correction search
    if tzolkin:
        t_val_target, t_name_idx_target = _parse_tzolkin(tzolkin)
        found = False
        for off in range(260):
            cfg.tzolkin_haab_correction.tzolkin = off
            if (julian_day_to_tzolkin_value(jdn) == t_val_target and
                julian_day_to_tzolkin_name_index(jdn) == t_name_idx_target):
                tz_offset = off
                found = True
                break
        if not found:
            raise ValueError('Unable to match tzolkin spec with any correction (0..259)')

    # Haab correction search
    if haab:
        h_day_target, h_month_target = _parse_haab(haab)
        found = False
        for off in range(365):
            cfg.tzolkin_haab_correction.haab = off
            packed = julian_day_to_haab_packed(jdn)
            hm = unpack_haab_month(packed)
            hd = unpack_haab_value(packed)
            if hm == h_month_target and hd == h_day_target:
                haab_offset = off
                found = True
                break
        if not found:
            raise ValueError('Unable to match haab spec with any correction (0..364)')

    # 9-day (g) correction
    if g_value is not None:
        found = False
        for off in range(9):
            cfg.tzolkin_haab_correction.g = off
            if julian_day_to_g_value(jdn) == g_value:
                g_offset = off
                found = True
                break
        if not found:
            raise ValueError('Unable to match g value 0..8')

    # Long count correction: parse long count like b.k.t.u.v.w or maybe missing leading b
    if long_count:
        parts = long_count.strip().split('.')
        lc_numbers = [int(p) for p in parts]
        if len(lc_numbers) == 5:  # Insert leading 1 like Pascal does
            lc_numbers = [1] + lc_numbers
        if len(lc_numbers) != 6:
            raise ValueError('Long Count must have 5 or 6 components separated by dots')
        # We simulate by varying lcd offset so computation matches target long count
        # Brute force a window of +/- 5000 days (heuristic)
        target = tuple(lc_numbers)
        found = False
        for off in range(-5000, 5001):
            cfg.tzolkin_haab_correction.lcd = off
            if julian_day_to_long_count(jdn) == target:
                lcd_offset = off
                found = True
                break
        if not found:
            raise ValueError('Unable to match long count within search window')

    # Year bearer reference
    yb_month = None
    yb_day = None
    if year_bearer:
        yb_val_target, yb_name_idx_target = _parse_year_bearer(year_bearer)
        # Need haab month/day of date for year bearer algorithm; we already can compute with current offsets
        # Search all 19*20 combos
        saved_month = cfg.year_bearer_str
        saved_day = cfg.year_bearer_val
        for m in range(19):
            for d in range(20):
                cfg.year_bearer_str = m
                cfg.year_bearer_val = d
                packed = year_bearer_packed(unpack_haab_month(julian_day_to_haab_packed(jdn)),
                                             unpack_haab_value(julian_day_to_haab_packed(jdn)), jdn, config=cfg)
                if unpack_yb_str(packed) == yb_name_idx_target and unpack_yb_val(packed) == yb_val_target:
                    yb_month = m
                    yb_day = d
                    break
            if yb_month is not None:
                break
        cfg.year_bearer_str = saved_month
        cfg.year_bearer_val = saved_day
        if yb_month is None:
            raise ValueError('Unable to derive year bearer reference')

    # 819-cycle station & value correction search (if either provided)
    if cycle819_station is not None or cycle819_value is not None:
        # We'll brute force station correction in reasonable window (-819..819)
        found = False
        for off in range(-819, 820):
            st = julian_day_to_819_station(jdn, off)
            val = julian_day_to_819_value(jdn, off)
            if cycle819_station is not None and st != cycle819_station:
                continue
            if cycle819_value is not None and val != cycle819_value:
                continue
            c819_station_corr = off
            found = True
            break
        if not found:
            raise ValueError('Unable to derive 819-cycle station/value correction')

    # Direction-color correction (if provided). We search 0..3 shift.
    if dir_color is not None:
        # Normalize like cycle819 module does
        from .cycle819 import _normalize as _norm, dir_col_str_to_val
        target_val = dir_col_str_to_val(dir_color)
        if target_val == 255:
            # attempt normalization fallback
            target_val = dir_col_str_to_val(_norm(dir_color))
        if target_val == 255:
            raise ValueError('Unknown direction/color spec')
        found = False
        for off in range(-4,5):
            st = julian_day_to_819_station(jdn, c819_station_corr)
            dc = station_to_dir_col(st, off)
            if dc == target_val:
                c819_dir_col_corr = off
                found = True
                break
        if not found:
            raise ValueError('Unable to derive direction/color correction')

    return AutoCorrectionResult(
        tzolkin_offset=tz_offset,
        haab_offset=haab_offset,
        g_offset=g_offset,
        lcd_offset=lcd_offset,
        year_bearer_month=yb_month,
        year_bearer_day=yb_day,
    cycle819_station_correction=c819_station_corr,
    cycle819_dir_color_correction=c819_dir_col_corr,
    )
