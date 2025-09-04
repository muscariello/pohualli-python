import subprocess, sys, json
from pohualli import (
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index, tzolkin_number_to_name,
    DEFAULT_CONFIG
)
from pohualli.cli import format_long_count

JDN = 2451545


def test_format_long_count():
    assert format_long_count((1,2,3,4,5,6)) == '1.2.3.4.5.6'


def test_cli_from_jdn_json_and_new_era_and_yearbear(tmp_path):
    # ensure year bearer ref applied
    cmd = [sys.executable,'-m','pohualli.cli','from-jdn',str(JDN),'--json','--new-era','584285','--year-bearer-ref','3','4']
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data['jdn'] == JDN


def test_cli_derive_autocorr():
    # build tzolkin spec
    val = julian_day_to_tzolkin_value(JDN)
    idx = julian_day_to_tzolkin_name_index(JDN)
    name = tzolkin_number_to_name(idx)
    spec = f"{val} {name}"
    cmd = [sys.executable,'-m','pohualli.cli','derive-autocorr',str(JDN),'--tzolkin',spec]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert 'tzolkin_offset' in out
