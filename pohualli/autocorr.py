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
from .types import TzolkinHaabCorrection, SheetWindowConfig, DEFAULT_CONFIG, CORRECTIONS, ABSOLUTE
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

def _tzolkin_value_with_offset(jdn: int, tz_off: int) -> int:
    day = jdn + tz_off + 2 + CORRECTIONS.cTzolkinVal
    if day < 0:
        day += (165191049 * 13)
    day_mod = ((day % 13) + 13) % 13
    day_mod += 4
    if day_mod > 13:
        day_mod -= 13
    return day_mod

def _tzolkin_name_index_with_offset(jdn: int, tz_off: int) -> int:
    day = jdn + tz_off + 2 + CORRECTIONS.cTzolkinStr
    if day < 0:
        day += (107374182 * 20)
    day_mod = ((day % 20) + 20) % 20
    day_mod += 15
    if day_mod >= 20:
        day_mod -= 20
    return day_mod

def _haab_packed_with_offset(jdn: int, haab_off: int) -> int:
    day = jdn + haab_off + 2 + CORRECTIONS.cHaabVal
    if day >= 0:
        day_mod = day % 365
        day_mod += 63
        if day_mod >= 365:
            day_mod -= 365
    else:
        day_abs = -day
        day_mod = day_abs % 365
        day_mod = 365 - (day_mod - 63)
        if day_mod >= 365:
            day_mod -= 365
    return day_mod

def _g_value_with_offset(jdn: int, g_off: int) -> int:
    day = jdn + g_off + 2 + CORRECTIONS.cGValue
    if day < 0:
        day += (238609294 * 9)
    day_mod = ((day % 9) + 9) % 9
    day_mod += 4
    if day_mod > 9:
        day_mod -= 9
    return day_mod

def _long_count_with_offset(jdn: int, lcd_off: int):
    day = jdn + lcd_off + 2 + CORRECTIONS.cLongCount
    counter = False
    new_era = ABSOLUTE.new_era
    if day < (new_era - 1872000):  # ERA_LENGTH
        counter = True
        day += (1145 * 1872000)
    day = day + (1872000 - new_era)
    out = []
    mult = 13 * 20 * 20 * 18 * 20
    b = day // mult; out.append(b); day -= b * mult
    mult = 20 * 20 * 18 * 20
    k = day // mult; out.append(k); day -= k * mult
    mult = 20 * 18 * 20
    t = day // mult; out.append(t); day -= t * mult
    mult = 18 * 20
    u = day // mult; out.append(u); day -= u * mult
    mult = 20
    v = day // mult; out.append(v)
    w = day - v * mult; out.append(w)
    if counter:
        out[0] -= 1145
    return tuple(out)  # type: ignore

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
            if (_tzolkin_value_with_offset(jdn, off) == t_val_target and
                _tzolkin_name_index_with_offset(jdn, off) == t_name_idx_target):
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
            packed = _haab_packed_with_offset(jdn, off)
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
            if _g_value_with_offset(jdn, off) == g_value:
                g_offset = off
                found = True
                break
        if not found:
            raise ValueError('Unable to match g value 0..8')

    # Long count correction: parse long count like b.k.t.u.v.w or maybe missing leading b
    if long_count:
        parts = long_count.strip().split('.')
        lc_numbers = [int(p) for p in parts]
        if len(lc_numbers) == 5:
            lc_numbers = [1] + lc_numbers
        if len(lc_numbers) != 6:
            raise ValueError('Long Count must have 5 or 6 components separated by dots')
        target = tuple(lc_numbers)
        found = False
        # Adaptive widening: first a quick small window, then a large window if needed.
        for window in (5000, 200000):
            for off in range(-window, window + 1):
                if _long_count_with_offset(jdn, off) == target:
                    lcd_offset = off
                    found = True
                    break
            if found:
                break
        if not found:
            raise ValueError(f'Unable to match long count within ±200000 day offset of JDN {jdn}')

    # Year bearer reference
    yb_month = None
    yb_day = None
    if year_bearer:
        yb_val_target, yb_name_idx_target = _parse_year_bearer(year_bearer)
        # compute target date haab components using derived haab_offset (if any search performed else 0)
        packed_date = _haab_packed_with_offset(jdn, haab_offset)
        date_hm = unpack_haab_month(packed_date)
        date_hd = unpack_haab_value(packed_date)
        date_pack = (date_hm * 20) + date_hd
        for m in range(19):
            for d in range(20):
                yb_pack = (m * 20) + d
                interval = date_pack - yb_pack
                if interval < 0:
                    interval += 365
                if DEFAULT_CONFIG.t_aztec:
                    interval -= 364
                base_jdn = jdn - interval
                name_idx = _tzolkin_name_index_with_offset(base_jdn, tz_offset)
                val = _tzolkin_value_with_offset(base_jdn, tz_offset)
                if name_idx == yb_name_idx_target and val == yb_val_target:
                    yb_month = m
                    yb_day = d
                    break
            if yb_month is not None:
                break
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
