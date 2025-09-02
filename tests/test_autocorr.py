from pohualli import derive_auto_corrections, compute_composite
from pohualli import (
    julian_day_to_819_station, julian_day_to_819_value, station_to_dir_col,
    dir_col_val_to_str
)
from pohualli.types import SheetWindowConfig
from pohualli.composite import save_config, load_config, DEFAULT_CONFIG
from pathlib import Path
import json, tempfile

# Simple smoke test: provide known tzolkin/haab for a date and verify offsets returned are in valid ranges

def test_autocorr_basic():
    jdn = 2451545  # 2000-01-01
    comp = compute_composite(jdn)
    tz_spec = f"{comp.tzolkin_value} {comp.tzolkin_name}"  # e.g., '11 Ik'
    haab_spec = f"{comp.haab_day} {comp.haab_month_name}"  # '0 Pop'
    res = derive_auto_corrections(jdn, tzolkin=tz_spec, haab=haab_spec, g_value=None)
    assert 0 <= res.tzolkin_offset < 260
    assert 0 <= res.haab_offset < 365
    # If computed with same comp, offsets may simply match defaults (0) which is fine


def test_autocorr_819_and_dir_color():
    jdn = 2451545
    # Choose non-zero corrections
    station_off = 137
    dir_color_off = -2
    # Derive target station/value/dir_color produced by these corrections
    station = julian_day_to_819_station(jdn, station_off)
    value = julian_day_to_819_value(jdn, station_off)
    dir_color_val = station_to_dir_col(station, dir_color_off)
    dir_color_str = dir_col_val_to_str(dir_color_val)
    # Run derivation
    res = derive_auto_corrections(
        jdn,
        cycle819_station=station,
        cycle819_value=value,
        dir_color=dir_color_str,
    )
    assert res.cycle819_station_correction == station_off
    assert res.cycle819_dir_color_correction == dir_color_off

def test_persistence_cycle819_fields(tmp_path: Path):
    # modify config
    DEFAULT_CONFIG.cycle819_station_correction = 123
    DEFAULT_CONFIG.cycle819_dir_color_correction = -1
    cfg_file = tmp_path / 'cfg.json'
    save_config(cfg_file)
    # reset to zero then load
    DEFAULT_CONFIG.cycle819_station_correction = 0
    DEFAULT_CONFIG.cycle819_dir_color_correction = 0
    load_config(cfg_file)
    assert DEFAULT_CONFIG.cycle819_station_correction == 123
    assert DEFAULT_CONFIG.cycle819_dir_color_correction == -1
