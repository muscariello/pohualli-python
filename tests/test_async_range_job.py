import time
from fastapi.testclient import TestClient
from pohualli.webapp import app

client = TestClient(app)

def test_async_range_job_lifecycle():
    # Create a small job so it finishes quickly
    payload = {
        "start": 2451545,
        "end": 2451555,
        "step": 1,
        "limit": 5,
        "fields": "jdn,tzolkin_name,haab_month_name"
    }
    r = client.post('/api/range-jobs', json=payload)
    assert r.status_code == 200
    data = r.json()
    jid = data['id']
    assert data['status'] in ("pending","running","completed")

    # Poll until completion (should be fast)
    for _ in range(60):  # up to ~3s
        sr = client.get(f'/api/range-jobs/{jid}')
        assert sr.status_code == 200
        jd = sr.json()
        if jd['status'] in ('completed','error','canceled'):
            # basic invariants
            assert jd['scanned'] > 0
            assert jd['count'] <= 5
            assert len(jd['matches']) == jd['count']
            assert jd['fields'][:3] == ['jdn','tzolkin_name','haab_month_name']
            assert jd['status'] == 'completed', jd
            break
        time.sleep(0.05)
    else:
        raise AssertionError('Job did not finish in time')
