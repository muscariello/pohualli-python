from __future__ import annotations
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from .composite import compute_composite
from .types import DEFAULT_CONFIG, ABSOLUTE
from .types import DEFAULT_CONFIG
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

@app.get('/health')
async def health():
    return {'status':'ok'}

@app.get('/', response_class=HTMLResponse)
async def home(request: Request, jdn: int | None = None, new_era: int | None = None,
               ybm: int | None = None, ybd: int | None = None):
    error = None
    comp = None
    if new_era is not None:
        ABSOLUTE.new_era = new_era
    if ybm is not None and ybd is not None:
        DEFAULT_CONFIG.year_bearer_str = ybm
        DEFAULT_CONFIG.year_bearer_val = ybd
    if jdn is not None:
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
        'error': error
    })
