import io, json, tempfile, os
from contextlib import redirect_stdout
from pohualli.cli import main
from pohualli import (
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index, tzolkin_number_to_name,
    DEFAULT_CONFIG
)

JDN = 2451545

def run_cli(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        main(argv)
    return buf.getvalue()


def test_from_jdn_textual_and_options():
    out = run_cli(["from-jdn", str(JDN), "--new-era","584283","--year-bearer-ref","2","3"])
    assert "JDN 2451545" in out
    assert "Tzolkin:" in out and "Haab:" in out and "Long Count:" in out and "Year Bearer packed:" in out


def test_from_jdn_json():
    out = run_cli(["from-jdn", str(JDN), "--json"])
    data = json.loads(out)
    assert data["jdn"] == JDN


def test_list_correlations_and_apply():
    out = run_cli(["list-correlations"])  # should list multiple presets
    assert "default" in out and "gmt-584283" in out
    out2 = run_cli(["apply-correlation","gmt-584283"])
    assert "gmt-584283" in out2


def test_save_and_load_config_via_main():
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "cfg.json")
        run_cli(["save-config", path])
        # mutate defaults then reload
        DEFAULT_CONFIG.year_bearer_str = 0
        DEFAULT_CONFIG.year_bearer_val = 0
        run_cli(["load-config", path])
        # file content sanity
        with open(path,'r') as f:
            js = json.load(f)
        # Config JSON groups fields; ensure year bearer persisted under expected keys
        # Accept either top-level or nested depending on implementation evolution
        nested_vals = json.dumps(js)
        assert 'year_bearer_str' in nested_vals


def test_derive_autocorr_via_main():
    val = julian_day_to_tzolkin_value(JDN)
    idx = julian_day_to_tzolkin_name_index(JDN)
    name = tzolkin_number_to_name(idx)
    spec = f"{val} {name}"
    out = run_cli(["derive-autocorr", str(JDN), "--tzolkin", spec])
    data = json.loads(out)
    assert "tzolkin_offset" in data
