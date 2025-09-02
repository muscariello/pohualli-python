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
async def home(request: Request, jdn: int | None = None, new_era: int | None = None,
               ybm: int | None = None, ybd: int | None = None, preset: str | None = None,
               tz_off: int | None = None, tzn_off: int | None = None, haab_off: int | None = None,
               g_off: int | None = None, lcd_off: int | None = None, week_off: int | None = None,
               c819s: int | None = None, c819d: int | None = None):
    error = None
    comp = None
    if new_era is not None:
        ABSOLUTE.new_era = new_era
    if ybm is not None and ybd is not None:
        DEFAULT_CONFIG.year_bearer_str = ybm
        DEFAULT_CONFIG.year_bearer_val = ybd
    if preset:
        try:
            apply_preset(preset)
        except KeyError:
            error = f"Unknown preset '{preset}'"
    # Handle correction overrides
    if tz_off is not None:
        DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin = tz_off
    if tzn_off is not None:
        CORRECTIONS.cTzolkinStr = tzn_off
    if haab_off is not None:
        DEFAULT_CONFIG.tzolkin_haab_correction.haab = haab_off
    if g_off is not None:
        DEFAULT_CONFIG.tzolkin_haab_correction.g = g_off
    if lcd_off is not None:
        DEFAULT_CONFIG.tzolkin_haab_correction.lcd = lcd_off
    if week_off is not None:
        CORRECTIONS.cWeekCorrection = week_off
    if c819s is not None:
        DEFAULT_CONFIG.cycle819_station_correction = c819s
    if c819d is not None:
        DEFAULT_CONFIG.cycle819_dir_color_correction = c819d
    if jdn is not None and error is None:
        try:
            comp = compute_composite(jdn).to_dict()
        except Exception as e:  # broad catch for UI feedback
            error = str(e)
    return templates.TemplateResponse('index.html', {
        'request': request,
        'comp': comp,
        'new_era': new_era,
        'ybm': ybm,
        'ybd': ybd,
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
