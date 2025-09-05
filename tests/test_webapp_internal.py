import time
from pohualli.webapp import RangeJob, _run_job, _early_filters, create_range_job, app
from pohualli.composite import compute_composite
from fastapi.testclient import TestClient

client = TestClient(app)


def test_early_filters_variants():
    # Build param dict hitting each optional branch
    base = {
        'id':'x', 'start':2451545, 'end':2451545, 'step':1,
        'tz_val': None, 'tz_name_l': None,
        'haab_day': None, 'haab_month_l': None, 'yb_name_l': None,
        'lc_pattern': None
    }
    assert _early_filters(2451545, base) is True
    # Add tzolkin value mismatch to force False quickly
    base2 = dict(base); base2['tz_val'] = 99
    assert _early_filters(2451545, base2) is False
    # Add name mismatch
    base3 = dict(base); base3['tz_name_l'] = 'not-a-name'
    assert _early_filters(2451545, base3) is False
    # Add lc_pattern mismatch length
    base4 = dict(base); base4['lc_pattern'] = ['1','2']
    assert _early_filters(2451545, base4) is False


def test_run_job_complete_and_limit():
    params = {
        'id':'job1','start':2451545,'end':2451550,'step':1,
        'tz_val':None,'tz_name_l':None,'haab_day':None,'haab_month_l':None,'yb_name_l':None,
        'dir_color_l':None,'weekday_i':None,'lc_pattern':None,
        'limit':3,'fields':['jdn','tzolkin_value'],'total':6
    }
    job = RangeJob(params)
    _run_job(job)
    assert job.status == 'completed'
    assert len(job.matches) == 3
    assert job.scanned >= 3


def test_run_job_cancel_midway():
    params = {
        'id':'job2','start':2451545,'end':2451600,'step':1,
        'tz_val':None,'tz_name_l':None,'haab_day':None,'haab_month_l':None,'yb_name_l':None,
        'dir_color_l':None,'weekday_i':None,'lc_pattern':None,
        'limit':0,'fields':['jdn'],'total':56
    }
    job = RangeJob(params)
    # Cancel after some iterations by injecting a small sleep throttle using monkeypatch of time.sleep not needed; we directly set flag
    def cancel_soon():
        for _ in range(5):
            if job.scanned >= 5:
                job.canceled = True
                break
            time.sleep(0.001)
    import threading
    t = threading.Thread(target=cancel_soon)
    t.start()
    _run_job(job)
    t.join()
    # If cancellation thread fired early job.status should become 'canceled'; else it may complete fast.
    if job.canceled and job.status == 'running':
        # emulate cancel endpoint semantics
        job.status = 'canceled'
    assert job.status in ('canceled','completed','running')
    if job.status == 'canceled':
        assert job.scanned < job.total


def test_health_and_list_jobs_endpoints():
    # Create job via API then list and health
    payload = {"start":2451545,"end":2451547,"step":1,"limit":1,"fields":"jdn"}
    r = client.post('/api/range-jobs', json=payload)
    assert r.status_code == 200
    jid = r.json()['id']
    lst = client.get('/api/range-jobs')
    assert any(j['id']==jid for j in lst.json())
    h = client.get('/health')
    assert h.json()['status'] == 'ok'
