import json, tempfile, os
from pohualli import compute_composite, save_config, load_config, DEFAULT_CONFIG

def test_compute_composite_fields():
    comp = compute_composite(2451545)
    d = comp.to_dict()
    assert d['jdn'] == 2451545
    # Check presence of key fields
    for key in ['tzolkin_name','haab_month_name','long_count','star_zodiac_name']:
        assert key in d


def test_save_load_config_roundtrip():
    DEFAULT_CONFIG.year_bearer_str = 5
    DEFAULT_CONFIG.year_bearer_val = 10
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td,'conf.json')
        save_config(path)
        # mutate
        DEFAULT_CONFIG.year_bearer_str = 0
        DEFAULT_CONFIG.year_bearer_val = 0
        load_config(path)
        assert DEFAULT_CONFIG.year_bearer_str == 5
        assert DEFAULT_CONFIG.year_bearer_val == 10
