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

app = FastAPI(title="Pohualli Calendar API")

templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))

@app.get('/api/convert')
async def api_convert(jdn: int = Query(..., description="Julian Day Number"),
                      new_era: int | None = None,
                      year_bearer_month: int | None = None,
                      year_bearer_day: int | None = None):
    if new_era is not None:
        ABSOLUTE.new_era = new_era
    if year_bearer_month is not None and year_bearer_day is not None:
        DEFAULT_CONFIG.year_bearer_str = year_bearer_month
        DEFAULT_CONFIG.year_bearer_val = year_bearer_day
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

@app.get('/health')
async def health():
    return {'status':'ok'}

@app.get('/', response_class=HTMLResponse)
async def home(
    request: Request,
    jdn: int | None = None,
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
    if jdn is not None and error is None:
        try:
            comp = compute_composite(jdn).to_dict()
        except Exception as e:  # broad catch for UI feedback
            error = str(e)
    return templates.TemplateResponse('index.html', {
        'request': request,
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
    })
