import io, json
from contextlib import redirect_stdout
from pohualli import (
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index, tzolkin_number_to_name,
)
from pohualli.cli import format_long_count, main

JDN = 2451545


def test_format_long_count():
    assert format_long_count((1,2,3,4,5,6)) == '1.2.3.4.5.6'


def run_cli(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        main(argv)
    return buf.getvalue()


def test_cli_from_jdn_json_and_new_era_and_yearbear(tmp_path):
    out = run_cli(['from-jdn',str(JDN),'--json','--new-era','584285','--year-bearer-ref','3','4'])
    data = json.loads(out)
    assert data['jdn'] == JDN


def test_cli_derive_autocorr():
    # build tzolkin spec
    val = julian_day_to_tzolkin_value(JDN)
    idx = julian_day_to_tzolkin_name_index(JDN)
    name = tzolkin_number_to_name(idx)
    spec = f"{val} {name}"
    out = run_cli(['derive-autocorr',str(JDN),'--tzolkin',spec])
    data = json.loads(out)
    assert 'tzolkin_offset' in data
