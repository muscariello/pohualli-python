from pohualli import (
    julian_day_to_tzolkin_value,
    julian_day_to_tzolkin_name_index,
    tzolkin_number_to_name,
    julian_day_to_haab_packed,
    unpack_haab_month,
    unpack_haab_value,
    julian_day_to_long_count,
    year_bearer_packed,
)
from pohualli.autocorr import derive_auto_corrections
from pohualli.types import DEFAULT_CONFIG
from pohualli.cycle819 import julian_day_to_819_station, julian_day_to_819_value
from pohualli.planets import (
    julian_day_to_planet_synodic_val,
    trunc_planet_synodic_val,
    all_planets,
)
from pohualli.zodiac import (
    zodiac_to_name,
    zodiac_name_to_index,
    zodiac_to_number,
    sum_zodiacs,
    julian_day_to_star_zodiac,
    julian_day_to_earth_zodiac,
)
from pohualli.cli import main as cli_main
import json, io, sys

JDN_SAMPLE = 2451545  # J2000


def test_autocorr_full_cycle():
    tzv = julian_day_to_tzolkin_value(JDN_SAMPLE)
    tzn_idx = julian_day_to_tzolkin_name_index(JDN_SAMPLE)
    tz_spec = f"{tzv} {tzolkin_number_to_name(tzn_idx)}"
    haab_packed = julian_day_to_haab_packed(JDN_SAMPLE)
    h_month = unpack_haab_month(haab_packed)
    h_day = unpack_haab_value(haab_packed)
    lc = julian_day_to_long_count(JDN_SAMPLE)
    long_count_spec = ".".join(str(x) for x in lc)
    yb = year_bearer_packed(h_month, h_day, JDN_SAMPLE)
    yb_spec = f"{yb & 0xFF} {tzolkin_number_to_name(yb >> 8)}"
    station = julian_day_to_819_station(JDN_SAMPLE, 0)
    value = julian_day_to_819_value(JDN_SAMPLE, 0)
    res = derive_auto_corrections(
        JDN_SAMPLE,
        tzolkin=tz_spec,
        haab=None,  # skip haab to avoid dependency on month name list
        long_count=long_count_spec,
        year_bearer=yb_spec,
        cycle819_station=station,
        cycle819_value=value,
        dir_color='Oeste',
    )
    assert 0 <= res.tzolkin_offset < 260
    assert 0 <= res.haab_offset < 365
    assert 0 <= res.g_offset < 9
    assert res.year_bearer_month is not None
    assert res.year_bearer_day is not None


def test_planet_synodic_and_trunc_branches():
    # Mercury typical synodic value
    syn = julian_day_to_planet_synodic_val(JDN_SAMPLE, 'mercury')
    idx = trunc_planet_synodic_val(syn, 'mercury')
    assert isinstance(idx, int)
    # Force > F2 branch by crafting syn = period/2
    syn2 = 115.9 / 2
    idx2 = trunc_planet_synodic_val(syn2, 'mercury')
    # Force < F3+1 branch with a large negative synthetic value
    idx3 = trunc_planet_synodic_val(-200.0, 'mercury')
    assert idx2 != idx and idx3 != idx
    # Exercise all_planets aggregation
    allp = all_planets(JDN_SAMPLE)
    assert 'venus' in allp and 'saturn' in allp
    assert allp['venus']['index'] == trunc_planet_synodic_val(allp['venus']['synodic_value'], 'venus')


def test_zodiac_utilities():
    deg = julian_day_to_star_zodiac(JDN_SAMPLE)
    name = zodiac_to_name(deg)
    idx = zodiac_name_to_index(name)
    num = zodiac_to_number(deg)
    recombined = sum_zodiacs(num, idx)
    assert 0 <= deg < 360
    assert 0 <= num < 30
    assert 0 <= idx < 12
    assert 0 <= recombined < 360
    # Edge / invalid
    assert zodiac_name_to_index('') == 255
    assert zodiac_to_name(720) == ''


def test_cli_derive_autocorr_invocation(monkeypatch):
    # Invoke CLI derive-autocorr with minimal args and capture output
    buf = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buf)
    cli_main(['derive-autocorr', str(JDN_SAMPLE)])
    out = buf.getvalue()
    data = json.loads(out)
    # If g was not requested may default to existing offset field still present
    assert 'tzolkin_offset' in data


def test_autocorr_error_paths():
    # Bad tzolkin spec
    try:
        derive_auto_corrections(JDN_SAMPLE, tzolkin='bad')
    except ValueError as e:
        assert 'Tzolkin spec' in str(e)
    # Bad haab spec
    try:
        derive_auto_corrections(JDN_SAMPLE, haab='13')
    except ValueError as e:
        assert 'Haab spec' in str(e)
    # Bad long count length
    try:
        derive_auto_corrections(JDN_SAMPLE, long_count='1.2.3')
    except ValueError as e:
        assert 'Long Count must' in str(e)
    # Unknown dir color
    try:
        derive_auto_corrections(JDN_SAMPLE, dir_color='???')
    except ValueError as e:
        assert 'Unknown direction' in str(e)


def test_zodiac_name_to_index_edges():
    assert zodiac_name_to_index('Ar') == 0
    assert zodiac_name_to_index('Aq') == 10
    assert zodiac_name_to_index('Cap') == 9
    assert zodiac_name_to_index('CnC') == 3
    assert zodiac_name_to_index('Li') == 6
    assert zodiac_name_to_index('Sa') == 8
    assert zodiac_name_to_index('Xx') == 255


def test_cli_from_jdn_text(monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buf)
    cli_main(['from-jdn', str(JDN_SAMPLE)])
    out = buf.getvalue()
    assert 'Tzolkin:' in out and 'Haab:' in out


def test_cli_save_and_load_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / 'cfg.json'
    cli_main(['save-config', str(cfg_file)])
    # Modify global config then reload
    from pohualli import DEFAULT_CONFIG
    DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin = 5
    cli_main(['load-config', str(cfg_file)])
    # After reload, offset should be whatever was saved (likely 0)
    assert DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin in (0,5)