from fastapi.testclient import TestClient
from pohualli.webapp import app

client = TestClient(app)

BASE = {"start":2451545,"end":2451555,"step":1,"fields":"jdn"}

def make(payload):
    r = client.post('/api/range-jobs', json=payload)
    assert r.status_code == 200
    return r.json()['id']


def wait(jid):
    import time
    for _ in range(80):
        d = client.get(f'/api/range-jobs/{jid}').json()
        if d['status'] in ('completed','error','canceled'):
            return d
        time.sleep(0.02)
    raise AssertionError('timeout')


def test_job_with_each_filter_type():
    # tzolkin value filter
    jid1 = make({**BASE, "tzolkin_value":1, "limit":1})
    d1 = wait(jid1); assert d1['status']=='completed'
    # tzolkin name filter
    jid2 = make({**BASE, "tzolkin_name":"Imix", "limit":1})
    d2 = wait(jid2); assert d2['status']=='completed'
    # haab day filter
    jid3 = make({**BASE, "haab_day":0, "limit":1})
    d3 = wait(jid3); assert d3['status']=='completed'
    # haab month filter (common month) maybe Pop
    jid4 = make({**BASE, "haab_month":"Pop", "limit":1})
    d4 = wait(jid4); assert d4['status']=='completed'
    # year bearer name filter
    jid5 = make({**BASE, "year_bearer_name":"Imix", "limit":1})
    d5 = wait(jid5); assert d5['status']=='completed'
    # weekday filter (1=Mon)
    jid6 = make({**BASE, "weekday":1, "limit":1})
    d6 = wait(jid6); assert d6['status']=='completed'
    # long count wildcard pattern
    jid7 = make({**BASE, "long_count":"*.*.*.*.*.*", "limit":1})
    d7 = wait(jid7); assert d7['status']=='completed'
    # dir_color substring filter (choose substring likely present like 'Norte' may need localization; use 'n' lowercase as broad)
    jid8 = make({**BASE, "dir_color":"n", "limit":1})
    d8 = wait(jid8); assert d8['status']=='completed'
