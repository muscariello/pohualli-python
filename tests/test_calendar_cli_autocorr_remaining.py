import json, subprocess, sys, os
from pohualli import weekday
from pohualli.calendar_dates import jdn_to_gregorian, jdn_to_julian, jdn_to_gregorian_pascal, gregorian_correction_pascal, format_date
from pohualli.types import CORRECTIONS
from pohualli.autocorr import derive_auto_corrections

JDN = 2451545  # 2000-01-01

def test_calendar_dates_variants():
    # baseline conversions
    g_std = jdn_to_gregorian(JDN)
    g_pas = jdn_to_gregorian_pascal(JDN)
    j_jul = jdn_to_julian(JDN)
    assert isinstance(g_std, tuple) and len(g_std) == 3
    assert isinstance(g_pas, tuple) and len(g_pas) == 3
    assert isinstance(j_jul, tuple) and len(j_jul) == 3
    # gregorian correction symmetry tweak by modifying week correction
    old = CORRECTIONS.cWeekCorrection
    CORRECTIONS.cWeekCorrection = 2
    try:
        wd = weekday(JDN)
        assert 1 <= wd <= 7
    finally:
        CORRECTIONS.cWeekCorrection = old
    # format
    assert format_date(g_std).count('-') == 2
    assert isinstance(gregorian_correction_pascal(JDN), int)


def test_cli_list_and_apply_correlations(tmp_path):
    # list-correlations
    out = subprocess.run([sys.executable,'-m','pohualli.cli','list-correlations'],capture_output=True,text=True)
    assert out.returncode == 0 and 'default' in out.stdout
    # apply-correlation
    out2 = subprocess.run([sys.executable,'-m','pohualli.cli','apply-correlation','default'],capture_output=True,text=True)
    assert out2.returncode == 0 and 'Applied correlation' in out2.stdout


def test_cli_save_and_load_config(tmp_path):
    path = tmp_path/'cfg.json'
    save = subprocess.run([sys.executable,'-m','pohualli.cli','save-config',str(path)],capture_output=True,text=True)
    assert save.returncode == 0
    load = subprocess.run([sys.executable,'-m','pohualli.cli','load-config',str(path)],capture_output=True,text=True)
    assert load.returncode == 0


def test_autocorr_helper_paths():
    # Provide tzolkin, haab, g together to drive combined loops
    # Use composite from current offsets
    from pohualli import julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index, tzolkin_number_to_name
    from pohualli import julian_day_to_haab_packed, unpack_haab_month, unpack_haab_value, haab_number_to_name, julian_day_to_g_value
    tv = julian_day_to_tzolkin_value(JDN)
    ti = julian_day_to_tzolkin_name_index(JDN)
    tn = tzolkin_number_to_name(ti)
    tz_spec = f"{tv} {tn}"
    packed = julian_day_to_haab_packed(JDN)
    hm = unpack_haab_month(packed)
    hv = unpack_haab_value(packed)
    haab_spec = f"{hv} {haab_number_to_name(hm)}"
    g_val = julian_day_to_g_value(JDN)
    res = derive_auto_corrections(JDN, tzolkin=tz_spec, haab=haab_spec, g_value=g_val)
    assert res.tzolkin_offset >= 0 and res.haab_offset >= 0 and res.g_offset >= 0
