from fastapi.testclient import TestClient
from pohualli.webapp import app

client = TestClient(app)

# Exercise deeper template branches: single conversion + range search + corrections all together

def test_home_single_and_range_combined_all_filters():
    params = {
        'jdn':'2451545',
        'r_start':'2451545','r_end':'2451555','r_tzval':'1','r_limit':'2','r_tzname':'Imix',
        'r_haab_day':'0','r_haab_month':'Pop','r_year_bearer_name':'Imix','r_dir_color':'Sur','r_weekday':'1','r_long_count':'*.*.*.*.*.*',
        'tz_off':'1','tzn_off':'1','haab_off':'1','g_off':'1','lcd_off':'1','week_off':'1','c819s':'1','c819d':'1'
    }
    r = client.get('/', params=params)
    assert r.status_code == 200
    # Ensure both composite and range table indicators appear
    text = r.text.lower()
    assert 'tzolkin' in text
    assert 'range' in text or 'jdn' in text


def test_home_range_only_with_limit_and_custom_fields():
    params = {
        'r_start':'2451545','r_end':'2451560','r_limit':'1','r_fields':'jdn,tzolkin_name,haab_month_name'
    }
    r = client.get('/', params=params)
    assert r.status_code == 200
    assert 'tzolkin' in r.text.lower()
    assert 'jdn' in r.text.lower()
