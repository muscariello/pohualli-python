import time
from fastapi.testclient import TestClient
from pohualli.webapp import app

client = TestClient(app)

def wait_job(jid, timeout=3.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.get(f'/api/range-jobs/{jid}')
        jd = r.json()
        if jd['status'] in ('completed','error','canceled'):
            return jd
        time.sleep(0.05)
    raise AssertionError('timeout waiting job')


def test_range_job_limit_truncates_matches():
    payload = {"start":2451545,"end":2451600,"step":1,"limit":3,"fields":"jdn"}
    r = client.post('/api/range-jobs', json=payload); assert r.status_code == 200
    jid = r.json()['id']
    jd = wait_job(jid)
    assert jd['status'] == 'completed'
    assert jd['count'] == 3


def test_range_job_dir_color_and_weekday_filters_zero():
    # Use improbable combination making zero matches likely within tiny span
    payload = {"start":2451545,"end":2451550,"step":1,"fields":"jdn","dir_color":"invalid-dir-color-substr","weekday":2}
    r = client.post('/api/range-jobs', json=payload); jid = r.json()['id']
    jd = wait_job(jid)
    assert jd['status'] == 'completed'
    # Zero matches expected
    assert jd['count'] == 0

