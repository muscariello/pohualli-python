from pohualli import (
    julian_day_to_819_station, julian_day_to_819_value, station_to_dir_col,
    dir_col_str_to_val, dir_col_val_to_str,
    year_bearer_packed, unpack_yb_str, unpack_yb_val,
    julian_day_to_maya_moon, str_maya_moon, julian_day_to_abn_dist, str_abn_dist, ecliptic,
)
from pohualli.correlations import apply_preset, active_preset_name
from pohualli.types import DEFAULT_CONFIG, ABSOLUTE


def test_819_negative_station_branch():
    # choose a jdn well before FIRST_JDN to hit branch paths when combined with negative correction
    jdn = 100000
    st = julian_day_to_819_station(jdn, -900)  # forces negative station adjustments
    val = julian_day_to_819_value(jdn, -900)
    # station may be negative; ensure function returns an int
    assert isinstance(st, int)
    # direction color with negative station path
    dc = station_to_dir_col(st, -5)
    # Function guarantees positive int; for negative station path it can still map into 1..4, accept any small positive
    assert isinstance(dc, int) and dc > 0
    # fuzzy dir color lookup partial prefix
    s = dir_col_val_to_str(dc)
    assert dir_col_str_to_val(s[:4]) in (1,2,3,4)


def test_year_bearer_aztec_interval_adjust():
    # enable aztec to exercise interval -= 364 logic
    DEFAULT_CONFIG.t_aztec = True
    try:
        DEFAULT_CONFIG.year_bearer_str = 1
        DEFAULT_CONFIG.year_bearer_val = 2
        yb = year_bearer_packed(haab_str=5, haab_val=10, jdn=2451545)
        assert isinstance(yb, int)
        assert unpack_yb_str(yb) >= 0
        assert unpack_yb_val(yb) >= 0
    finally:
        DEFAULT_CONFIG.t_aztec = False


def test_moon_early_date_branches():
    # pick date before both first day markers
    early = ABSOLUTE.maya_moon_first_day - 10
    mm = julian_day_to_maya_moon(early)
    ab = julian_day_to_abn_dist(ABSOLUTE.abn_dist_first_day - 10)
    smm = str_maya_moon(mm)
    sab = str_abn_dist(ab)
    assert 1 <= smm <= 30
    assert isinstance(sab, int)
    # ensure ecliptic bool path (likely false here) still returns bool
    assert isinstance(ecliptic(mm, ab), bool)


def test_apply_correlation_preset_switch():
    apply_preset('default')
    start = ABSOLUTE.new_era
    apply_preset('gmt-584283')
    assert active_preset_name() == 'gmt-584283'
    assert ABSOLUTE.new_era != start
    # switch back
    apply_preset('default')
    assert active_preset_name() == 'default'
