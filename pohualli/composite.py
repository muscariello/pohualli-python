# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any
from . import (
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index, tzolkin_number_to_name,
    julian_day_to_haab_packed, unpack_haab_month, unpack_haab_value, haab_number_to_name,
    julian_day_to_long_count, year_bearer_packed, unpack_yb_str, unpack_yb_val,
    julian_day_to_819_station, julian_day_to_819_value, station_to_dir_col, dir_col_val_to_str,
    julian_day_to_planet_synodic_val, trunc_planet_synodic_val, P_MERCURY, P_VENUS,
    julian_day_to_maya_moon, julian_day_to_abn_dist, ecliptic,
    julian_day_to_star_zodiac, julian_day_to_earth_zodiac, zodiac_to_name
)
from .types import DEFAULT_CONFIG, ABSOLUTE, CORRECTIONS, AbsoluteCorrections, SheetWindowConfig, CorrectionRecord
from .correlations import active_preset_name
from .calendar_dates import jdn_to_gregorian, jdn_to_julian, weekday, format_date

@dataclass
class CompositeResult:
    jdn: int
    tzolkin_value: int
    tzolkin_name_index: int
    tzolkin_name: str
    haab_day: int
    haab_month_index: int
    haab_month_name: str
    long_count: tuple
    year_bearer_packed: int
    year_bearer_name_index: int
    year_bearer_value: int
    year_bearer_name: str
    cycle819_station: int
    cycle819_value: int
    dir_color_val: int
    dir_color_str: str
    mercury_synodic: float
    mercury_index: int
    venus_synodic: float
    venus_index: int
    maya_moon_age: float
    abnormal_distance: float
    eclipse_possible: bool
    star_zodiac_deg: int
    star_zodiac_name: str
    earth_zodiac_deg: int
    earth_zodiac_name: str
    gregorian_date: str | None = None
    julian_date: str | None = None
    iso_weekday: int | None = None
    # Extended planets (optional)
    mars_synodic: float | None = None
    mars_index: int | None = None
    jupiter_synodic: float | None = None
    jupiter_index: int | None = None
    saturn_synodic: float | None = None
    saturn_index: int | None = None
    uranus_synodic: float | None = None
    uranus_index: int | None = None
    neptune_synodic: float | None = None
    neptune_index: int | None = None
    pluto_synodic: float | None = None
    pluto_index: int | None = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def compute_composite(jdn: int, *, config: SheetWindowConfig | None = None) -> CompositeResult:
    cfg = config or DEFAULT_CONFIG
    tzv = julian_day_to_tzolkin_value(jdn)
    tzn = julian_day_to_tzolkin_name_index(jdn)
    tzname = tzolkin_number_to_name(tzn)
    haab_packed = julian_day_to_haab_packed(jdn)
    haab_month = unpack_haab_month(haab_packed)
    haab_day = unpack_haab_value(haab_packed)
    haab_name = haab_number_to_name(haab_month)
    lc = julian_day_to_long_count(jdn)
    yb = year_bearer_packed(haab_month, haab_day, jdn, config=cfg)
    yb_name = unpack_yb_str(yb)
    yb_val = unpack_yb_val(yb)
    c819_station = julian_day_to_819_station(jdn, cfg.cycle819_station_correction)
    c819_value = julian_day_to_819_value(jdn, cfg.cycle819_station_correction)
    dir_col = station_to_dir_col(c819_station, cfg.cycle819_dir_color_correction)
    dir_col_str = dir_col_val_to_str(dir_col)
    merc_syn = julian_day_to_planet_synodic_val(jdn, P_MERCURY)
    merc_idx = trunc_planet_synodic_val(merc_syn, P_MERCURY)
    venus_syn = julian_day_to_planet_synodic_val(jdn, P_VENUS)
    venus_idx = trunc_planet_synodic_val(venus_syn, P_VENUS)
    # Additional planets
    mars_syn = julian_day_to_planet_synodic_val(jdn, 3)
    mars_idx = trunc_planet_synodic_val(mars_syn, 3)
    jup_syn = julian_day_to_planet_synodic_val(jdn, 4)
    jup_idx = trunc_planet_synodic_val(jup_syn, 4)
    sat_syn = julian_day_to_planet_synodic_val(jdn, 5)
    sat_idx = trunc_planet_synodic_val(sat_syn, 5)
    ura_syn = julian_day_to_planet_synodic_val(jdn, 6)
    ura_idx = trunc_planet_synodic_val(ura_syn, 6)
    nep_syn = julian_day_to_planet_synodic_val(jdn, 7)
    nep_idx = trunc_planet_synodic_val(nep_syn, 7)
    plu_syn = julian_day_to_planet_synodic_val(jdn, 8)
    plu_idx = trunc_planet_synodic_val(plu_syn, 8)
    mm_age = julian_day_to_maya_moon(jdn)
    abd = julian_day_to_abn_dist(jdn)
    eclipse_flag = ecliptic(mm_age, abd)
    star_z = julian_day_to_star_zodiac(jdn)
    earth_z = julian_day_to_earth_zodiac(jdn)
    star_name = zodiac_to_name(star_z)
    earth_name = zodiac_to_name(earth_z)
    g_y,g_m,g_d = jdn_to_gregorian(jdn)
    j_y,j_m,j_d = jdn_to_julian(jdn)
    wd = weekday(jdn)
    yb_tz_name = tzolkin_number_to_name(yb_name)
    return CompositeResult(
        jdn=jdn,
        tzolkin_value=tzv,
        tzolkin_name_index=tzn,
        tzolkin_name=tzname,
        haab_day=haab_day,
        haab_month_index=haab_month,
        haab_month_name=haab_name,
        long_count=lc,
        year_bearer_packed=yb,
        year_bearer_name_index=yb_name,
    year_bearer_value=yb_val,
    year_bearer_name=yb_tz_name,
        cycle819_station=c819_station,
        cycle819_value=c819_value,
        dir_color_val=dir_col,
        dir_color_str=dir_col_str,
        mercury_synodic=merc_syn,
        mercury_index=merc_idx,
    venus_synodic=venus_syn,
    venus_index=venus_idx,
    mars_synodic=mars_syn,
    mars_index=mars_idx,
    jupiter_synodic=jup_syn,
    jupiter_index=jup_idx,
    saturn_synodic=sat_syn,
    saturn_index=sat_idx,
    uranus_synodic=ura_syn,
    uranus_index=ura_idx,
    neptune_synodic=nep_syn,
    neptune_index=nep_idx,
    pluto_synodic=plu_syn,
    pluto_index=plu_idx,
        maya_moon_age=mm_age,
        abnormal_distance=abd,
        eclipse_possible=eclipse_flag,
        star_zodiac_deg=star_z,
        star_zodiac_name=star_name,
        earth_zodiac_deg=earth_z,
    earth_zodiac_name=earth_name,
    gregorian_date=format_date((g_y,g_m,g_d)),
    julian_date=format_date((j_y,j_m,j_d)),
    iso_weekday=wd,
    )

# Persistence ---------------------------------------------------------------------------------

import json
from pathlib import Path

@dataclass
class PersistedConfig:
    config: SheetWindowConfig
    corrections: CorrectionRecord
    absolute: AbsoluteCorrections

    def to_dict(self):
        return {
            'config': vars(self.config),
            'corrections': vars(self.corrections),
            'absolute': vars(self.absolute),
            'correlation_preset': active_preset_name(),
        }


def save_config(path: str | Path):
    def serialize(obj):
        if hasattr(obj, '__dict__'):
            return {k: serialize(v) for k,v in vars(obj).items()}
        return obj
    data = serialize(PersistedConfig(DEFAULT_CONFIG, CORRECTIONS, ABSOLUTE))
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True))


def load_config(path: str | Path):
    p = Path(path)
    data = json.loads(p.read_text())
    cfg_d = data.get('config', {})
    for k,v in cfg_d.items():
        if k == 'tzolkin_haab_correction' and isinstance(v, dict):
            # nested dataclass fields
            for nk,nv in v.items():
                setattr(DEFAULT_CONFIG.tzolkin_haab_correction, nk, nv)
        else:
            setattr(DEFAULT_CONFIG, k, v)
    corr_d = data.get('corrections', {})
    for k,v in corr_d.items():
        setattr(CORRECTIONS, k, v)
    abs_d = data.get('absolute', {})
    for k,v in abs_d.items():
        setattr(ABSOLUTE, k, v)
