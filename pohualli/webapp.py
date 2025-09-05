# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from .composite import compute_composite
from .autocorr import derive_auto_corrections
from .types import DEFAULT_CONFIG, ABSOLUTE, CORRECTIONS
from .correlations import list_presets, apply_preset, active_preset_name
from pathlib import Path
from pydantic import BaseModel
import threading, uuid, time, logging, os

logger = logging.getLogger("pohualli")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# ---------------- Range Search Async Job Management -----------------
class RangeJob:
    def __init__(self, params: dict):
        # Identity & original parameters
        self.id: str = params['id']
        self.params: dict = params

        # Promoted frequently accessed params
        self.start: int | None = params.get('start')
        self.end: int | None = params.get('end')
        self.step: int | None = params.get('step')

        # Lifecycle / status
        self.status: str = 'pending'
        self.error: str | None = None
        self.canceled: bool = False
        self.started: float = time.time()
        self.ended: float | None = None

        # Progress & limits
        self.scanned: int = 0
        self.total: int = int(params.get('total', 0))
        self.limit: int = int(params.get('limit', 0))

        # Result shaping
        self.fields: list[str] = list(params.get('fields', []))
        self.matches: list[dict] = []

        # Execution thread
        self.thread: threading.Thread | None = None

    def to_dict(self) -> dict:
        elapsed = (self.ended or time.time()) - self.started
        base = {
            'id': self.id,
            'status': self.status,
            'error': self.error,
            'scanned': self.scanned,
            'total': self.total,
            'matches': self.matches,
            'count': len(self.matches),
            'fields': self.fields,
            'limit': self.limit,
            'canceled': self.canceled,
            'elapsed': elapsed,
            'partial': self.status == 'canceled' and self.scanned < self.total,
            'start': self.start,
            'end': self.end,
            'step': self.step,
            'started': self.started,
            'ended': self.ended,
        }
        # Legacy alternate keys for front-end fallback
        base['range_start'] = base['start']
        base['range_end'] = base['end']
        base['step_size'] = base['step']
        return base

JOBS: dict[str, RangeJob] = {}
JOBS_LOCK = threading.Lock()

def _early_filters(jdn: int, p: dict) -> bool:
    # Early cheap filters using primitive functions
    from . import (
        julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index,
        tzolkin_number_to_name, julian_day_to_haab_packed, unpack_haab_month,
        unpack_haab_value, haab_number_to_name, julian_day_to_long_count,
        year_bearer_packed, tzolkin_number_to_name as _tzname
    )
    tz_val = p.get('tz_val')
    tz_name_l = p.get('tz_name_l')
    haab_day = p.get('haab_day')
    haab_month_l = p.get('haab_month_l')
    yb_name_l = p.get('yb_name_l')
    lc_pattern = p.get('lc_pattern')
    if tz_val or tz_name_l:
        v = julian_day_to_tzolkin_value(jdn)
        if tz_val and v != tz_val:
            return False
        if tz_name_l:
            nidx = julian_day_to_tzolkin_name_index(jdn)
            if tzolkin_number_to_name(nidx).lower() != tz_name_l:
                return False
    need_haab = haab_day is not None or haab_month_l or yb_name_l
    if need_haab:
        packed = julian_day_to_haab_packed(jdn)
        m = unpack_haab_month(packed)
        d = unpack_haab_value(packed)
        if haab_day is not None and d != haab_day:
            return False
        if haab_month_l and haab_number_to_name(m).lower() != haab_month_l:
            return False
        if yb_name_l:
            yb = year_bearer_packed(m, d, jdn)
            if _tzname(yb >> 8).lower() != yb_name_l:
                return False
    if lc_pattern:
        lc = julian_day_to_long_count(jdn)
        if len(lc_pattern) != len(lc):
            return False
        for pat, val in zip(lc_pattern, lc):
            if pat != '*' and pat != str(val):
                return False
    return True

def _run_job(job: RangeJob):
    p = job.params
    start = p['start']; end = p['end']; step = p['step']
    dir_color_l = p.get('dir_color_l'); weekday_i = p.get('weekday_i')
    limit = job.limit
    from .composite import compute_composite
    job.status = 'running'
    try:
        for jdn in range(start, end+1, step):
            if job.canceled:
                # Respect user cancellation; do not overwrite status later
                break
            job.scanned += 1
            # Cooperative yield so cancellation requests can interleave; minimal overhead.
            if job.scanned % 250 == 0:
                time.sleep(0)  # yield GIL without significant delay
            # Optional throttle (set POHUALLI_RANGE_THROTTLE microseconds) for testing cancellation determinism
            if THROTTLE_US:
                time.sleep(THROTTLE_US / 1_000_000.0)
            if not _early_filters(jdn, p):
                continue
            comp = compute_composite(jdn)
            if dir_color_l and dir_color_l not in comp.dir_color_str.lower():
                continue
            if weekday_i and comp.iso_weekday != weekday_i:
                continue
            row = {}
            for f in job.fields:
                v = getattr(comp, f, '')
                if isinstance(v, (list, tuple)):
                    v = '.'.join(str(x) for x in v)
                row[f] = v
            job.matches.append(row)
            if limit and len(job.matches) >= limit:
                break
        if not job.canceled and job.status != 'canceled':
            job.status = 'completed'
    except Exception as e:  # pragma: no cover (rare)
        job.error = str(e)
        job.status = 'error'
    finally:
        job.ended = time.time()


app = FastAPI(title="Pohualli Calendar API")

# Read optional throttle env once (int microseconds); keep small (e.g., 200) during tests to allow cancel window
try:
    THROTTLE_US = int(os.environ.get('POHUALLI_RANGE_THROTTLE','0'))
except ValueError:
    THROTTLE_US = 0

templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))

class RangeJobRequest(BaseModel):
    start: int
    end: int
    step: int = 1
    limit: int = 0
    tzolkin_value: int | None = None
    tzolkin_name: str | None = None
    haab_day: int | None = None
    haab_month: str | None = None
    year_bearer_name: str | None = None
    dir_color: str | None = None
    weekday: int | None = None
    long_count: str | None = None
    fields: str | None = None

@app.post('/api/range-jobs')
async def create_range_job(req: RangeJobRequest):
    start = req.start; end = req.end; step = req.step; limit = req.limit
    if end < start:
        start, end = end, start
    step = step if step > 0 else 1
    lc_pattern = req.long_count.split('.') if req.long_count else None
    default_fields = ['jdn','gregorian_date','tzolkin_value','tzolkin_name','haab_day','haab_month_name','long_count','year_bearer_name','dir_color_str']
    fld_list = [f.strip() for f in (req.fields.split(',') if req.fields else default_fields) if f.strip()]
    total = ((end - start)//step)+1
    jid = uuid.uuid4().hex[:12]
    params = {
        'id': jid,
        'start': start,
        'end': end,
        'step': step,
        'tz_val': req.tzolkin_value,
        'tz_name_l': req.tzolkin_name.lower() if req.tzolkin_name else None,
        'haab_day': req.haab_day,
        'haab_month_l': req.haab_month.lower() if req.haab_month else None,
        'yb_name_l': req.year_bearer_name.lower() if req.year_bearer_name else None,
        'dir_color_l': req.dir_color.lower() if req.dir_color else None,
        'weekday_i': req.weekday,
        'lc_pattern': lc_pattern,
        'limit': limit,
        'fields': fld_list,
        'total': total,
    }
    job = RangeJob(params)
    with JOBS_LOCK:
        JOBS[jid] = job
    t = threading.Thread(target=_run_job, args=(job,), daemon=True)
    job.thread = t
    t.start()
    return job.to_dict()

@app.get('/api/range-jobs/{jid}')
async def get_range_job(jid: str):
    job = JOBS.get(jid)
    if not job:
        return JSONResponse({'error':'not found'}, status_code=404)
    return job.to_dict()

@app.post('/api/range-jobs/{jid}/cancel')
async def cancel_range_job(jid: str):
    job = JOBS.get(jid)
    if not job:
        return JSONResponse({'error':'not found'}, status_code=404)
    # Mark cancellation and snapshot current state immediately.
    job.canceled = True
    # If currently running, mark status canceled now so client gets partial results without waiting loop break.
    if job.status in ('pending','running'):
        # Mark as canceled; partial flag derived in to_dict when scanned < total
        job.status = 'canceled'
        job.ended = time.time()
    return job.to_dict()

@app.get('/api/range-jobs')
async def list_range_jobs():
    with JOBS_LOCK:
        return [j.to_dict() for j in JOBS.values()]

@app.get('/api/convert')
async def api_convert(jdn: int = Query(..., description="Julian Day Number"),
                      new_era: int | None = None,
                      year_bearer_month: int | None = None,
                      year_bearer_day: int | None = None,
                      culture: str | None = Query(None, description="maya or aztec year bearer mode")):
    if new_era is not None:
        ABSOLUTE.new_era = new_era
    if year_bearer_month is not None and year_bearer_day is not None:
        DEFAULT_CONFIG.year_bearer_str = year_bearer_month
        DEFAULT_CONFIG.year_bearer_val = year_bearer_day
    if culture:
        DEFAULT_CONFIG.t_aztec = (culture.lower() == 'aztec')
    comp = compute_composite(jdn)
    return JSONResponse(comp.to_dict())

@app.get('/api/derive-autocorr')
async def api_derive_autocorr(jdn: int = Query(..., description="Julian Day Number"),
                              tzolkin: str | None = None,
                              haab: str | None = None,
                              g: int | None = None,
                              long_count: str | None = None,
                              year_bearer: str | None = None,
                              cycle819_station: int | None = None,
                              cycle819_value: int | None = None,
                              dir_color: str | None = None):
    """Brute-force derive correction offsets given target textual specs.
    Only provide the specs you want solved; others can be omitted.
    """
    try:
        res = derive_auto_corrections(
            jdn,
            tzolkin=tzolkin,
            haab=haab,
            g_value=g,
            long_count=long_count,
            year_bearer=year_bearer,
            cycle819_station=cycle819_station,
            cycle819_value=cycle819_value,
            dir_color=dir_color,
        )
        return JSONResponse(res.__dict__)
    except ValueError as ve:
        logger.info(
            "derive-autocorr value error jdn=%s tz=%s haab=%s g=%s lc=%s yb=%s st=%s val=%s dir=%s -> %s",
            jdn,
            tzolkin,
            haab,
            g,
            long_count,
            year_bearer,
            cycle819_station,
            cycle819_value,
            dir_color,
            ve,
        )
        return JSONResponse({'error': str(ve)}, status_code=400)
    except Exception as e:  # pragma: no cover
        logger.exception(
            "derive-autocorr internal error jdn=%s tz=%s haab=%s g=%s lc=%s yb=%s st=%s val=%s dir=%s",
            jdn,
            tzolkin,
            haab,
            g,
            long_count,
            year_bearer,
            cycle819_station,
            cycle819_value,
            dir_color,
        )
        return JSONResponse({'error': 'internal error', 'detail': str(e)}, status_code=500)

@app.get('/health')
async def health():
    return {'status':'ok'}

@app.get('/', response_class=HTMLResponse)
async def home(
    request: Request,
    jdn: str | None = None,
    # Accept optional numeric query params as strings so blank values ("") don't raise validation errors
    new_era: str | None = None,
    ybm: str | None = None,
    ybd: str | None = None,
    preset: str | None = None,
    tz_off: str | None = None,
    tzn_off: str | None = None,
    haab_off: str | None = None,
    g_off: str | None = None,
    lcd_off: str | None = None,
    week_off: str | None = None,
    c819s: str | None = None,
    c819d: str | None = None,
    culture: str | None = None,
    # Range search params (prefixed to avoid collision)
    r_start: str | None = None,
    r_end: str | None = None,
    r_tzval: str | None = None,
    r_tzname: str | None = None,
    r_haab_day: str | None = None,
    r_haab_month: str | None = None,
    r_year_bearer_name: str | None = None,
    r_dir_color: str | None = None,
    r_weekday: str | None = None,
    r_long_count: str | None = None,
    r_limit: str | None = None,
    r_step: str | None = None,
    r_fields: str | None = None,
):
    def _opt_int(v: str | None) -> int | None:
        if v is None or v == "":
            return None
        try:
            return int(v)
        except ValueError:
            return None  # silently ignore bad numeric input for now; could surface error message instead
    error = None
    comp = None
    new_era_i = _opt_int(new_era)
    jdn_i = _opt_int(jdn)
    ybm_i = _opt_int(ybm)
    ybd_i = _opt_int(ybd)
    if new_era_i is not None:
        ABSOLUTE.new_era = new_era_i
    if ybm_i is not None and ybd_i is not None:
        DEFAULT_CONFIG.year_bearer_str = ybm_i
        DEFAULT_CONFIG.year_bearer_val = ybd_i
    if preset:
        try:
            apply_preset(preset)
        except KeyError:
            error = f"Unknown preset '{preset}'"
    # Handle correction overrides
    tz_off_i = _opt_int(tz_off)
    tzn_off_i = _opt_int(tzn_off)
    haab_off_i = _opt_int(haab_off)
    g_off_i = _opt_int(g_off)
    lcd_off_i = _opt_int(lcd_off)
    week_off_i = _opt_int(week_off)
    c819s_i = _opt_int(c819s)
    c819d_i = _opt_int(c819d)
    if tz_off_i is not None:
        DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin = tz_off_i
    if tzn_off_i is not None:
        CORRECTIONS.cTzolkinStr = tzn_off_i
    if haab_off_i is not None:
        DEFAULT_CONFIG.tzolkin_haab_correction.haab = haab_off_i
    if g_off_i is not None:
        DEFAULT_CONFIG.tzolkin_haab_correction.g = g_off_i
    if lcd_off_i is not None:
        DEFAULT_CONFIG.tzolkin_haab_correction.lcd = lcd_off_i
    if week_off_i is not None:
        CORRECTIONS.cWeekCorrection = week_off_i
    if c819s_i is not None:
        DEFAULT_CONFIG.cycle819_station_correction = c819s_i
    if c819d_i is not None:
        DEFAULT_CONFIG.cycle819_dir_color_correction = c819d_i
    # Compute single date composite if requested
    if jdn_i is not None and error is None:
        try:
            comp = compute_composite(jdn_i).to_dict()
        except Exception as e:
            error = str(e)
    # Range search (independent of single conversion)
    range_results = None
    range_fields = None
    if (r_start not in (None, "")) and (r_end not in (None, "")) and error is None:
        rs: int | None = None
        re_: int | None = None
        try:
            rs = int(r_start); re_ = int(r_end)
        except ValueError:
            error = "Invalid range start/end"
        if error is None and rs is not None and re_ is not None:
            if rs > re_:
                rs, re_ = re_, rs
            step_i = _opt_int(r_step) or 1
            tz_val_i = _opt_int(r_tzval)
            tz_name_l = r_tzname.lower() if r_tzname else None
            haab_day_i = _opt_int(r_haab_day)
            haab_month_l = r_haab_month.lower() if r_haab_month else None
            yb_name_l = r_year_bearer_name.lower() if r_year_bearer_name else None
            dir_color_l = r_dir_color.lower() if r_dir_color else None
            weekday_i = _opt_int(r_weekday)
            lc_pattern = r_long_count.split('.') if r_long_count else None
            limit_i = _opt_int(r_limit) or 0
            default_fields = ['jdn','gregorian_date','tzolkin_value','tzolkin_name','haab_day','haab_month_name','long_count','year_bearer_name','dir_color_str']
            range_fields = [f.strip() for f in (r_fields.split(',') if r_fields else default_fields) if f.strip()]
            def match_lc(lc_tuple):
                if not lc_pattern:
                    return True
                if len(lc_pattern) != len(lc_tuple):
                    return False
                for pat,val in zip(lc_pattern, lc_tuple):
                    if pat != '*' and pat != str(val):
                        return False
                return True
            results = []
            scanned = 0
            for jdn_scan in range(rs, re_+1, step_i):  # type: ignore[arg-type]
                scanned += 1
                comp_obj = compute_composite(jdn_scan)
                if tz_val_i and comp_obj.tzolkin_value != tz_val_i:
                    continue
                if tz_name_l and comp_obj.tzolkin_name.lower() != tz_name_l:
                    continue
                if haab_day_i is not None and comp_obj.haab_day != haab_day_i:
                    continue
                if haab_month_l and comp_obj.haab_month_name.lower() != haab_month_l:
                    continue
                if yb_name_l and comp_obj.year_bearer_name.lower() != yb_name_l:
                    continue
                if dir_color_l and dir_color_l not in comp_obj.dir_color_str.lower():
                    continue
                if weekday_i and comp_obj.iso_weekday != weekday_i:
                    continue
                if not match_lc(comp_obj.long_count):
                    continue
                row = {}
                for f in range_fields:
                    v = getattr(comp_obj, f, '')
                    if isinstance(v, (list, tuple)):
                        v = '.'.join(str(x) for x in v)
                    row[f] = v
                results.append(row)
                if limit_i and len(results) >= limit_i:
                    break
            range_results = {
                'rows': results,
                'count': len(results),
                'scanned': scanned,
            }
    return templates.TemplateResponse(
        request,
        'index.html',
        {
            'comp': comp,
            'new_era': new_era_i,
            'ybm': ybm_i,
            'ybd': ybd_i,
            'corr': {
                'tzolkin': DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin,
                'tzolkin_name': CORRECTIONS.cTzolkinStr,
                'haab': DEFAULT_CONFIG.tzolkin_haab_correction.haab,
                'g': DEFAULT_CONFIG.tzolkin_haab_correction.g,
                'lcd': DEFAULT_CONFIG.tzolkin_haab_correction.lcd,
                'week': CORRECTIONS.cWeekCorrection,
                'c819_station': DEFAULT_CONFIG.cycle819_station_correction,
                'c819_dir': DEFAULT_CONFIG.cycle819_dir_color_correction,
            },
            'error': error,
            'presets': list_presets(),
            'active_preset': active_preset_name(),
            'culture': 'aztec' if DEFAULT_CONFIG.t_aztec else 'maya',
            'range': range_results,
            'range_fields': range_fields,
        }
    )
