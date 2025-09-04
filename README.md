# Pohualli (Python Port)

[![CI](https://github.com/muscariello/pohualli-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/muscariello/pohualli-python/actions/workflows/ci.yml) [![Coverage](https://codecov.io/gh/muscariello/pohualli-python/branch/main/graph/badge.svg)](https://codecov.io/gh/muscariello/pohualli-python) [![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://muscariello.github.io/pohualli-python/) [![Changelog](https://img.shields.io/badge/changelog-latest-orange)](CHANGELOG.md)

Work-in-progress Python reimplementation of the original Turbo Pascal Pohualli calendar utility.

## Goals

- Faithful translation of core calendrical calculations (Maya & Aztec systems)
- 819-day cycle, planetary synodic values, year bearer computation
- Configurable New Era and correction parameters
- Composite API producing structured results
- Config persistence (save/load JSON)
- Clear, testable Python modules separated from any UI
- Modern packaging & minimal dependencies

## Structure

```
pohualli/
  __init__.py
  autocorr.py          # Auto-derivation of correction offsets
  aztec.py             # Aztec-specific name tables & conversions
  calendar_dates.py    # Gregorian / Julian conversion helpers
  cli.py               # Command-line interface entry point
  composite.py         # High-level composite computation
  correlations.py      # Correlation preset management
  cycle819.py          # 819-day cycle station & value
  maya.py              # Core Tzolk'in / Haab / Long Count logic
  moon.py              # Moon age & eclipse heuristic
  planets.py           # Planet synodic computations
  templates/           # Web UI Jinja2 templates
  types.py             # Dataclasses for config & corrections
  webapp.py            # FastAPI application
  yearbear.py          # Year bearer packing/unpacking
  zodiac.py            # Star & earth zodiac logic
tests/
  test_autocorr.py
  test_calendar_parity.py
  test_composite.py
  test_cycle_planets.py
  test_maya.py
  test_moon_zodiac.py
  test_web.py
  test_yearbear_cli.py
docs/                  # MkDocs documentation sources
mkdocs.yml             # MkDocs configuration
Dockerfile
docker-compose.yml
pyproject.toml
LICENSE
README.md
```

## Composite Usage (Python)
```python
from pohualli import compute_composite
res = compute_composite(2451545)
print(res.tzolkin_name, res.long_count, res.star_zodiac_name)
```

## CLI Examples
```
# Human-readable
pohualli from-jdn 2451545 --year-bearer-ref 0 0
# JSON output
pohualli from-jdn 2451545 --json > result.json
# Override New Era
pohualli from-jdn 2451545 --new-era 584285 --json
# Save & load config
pohualli save-config config.json
pohualli load-config config.json
```

## Tests
```
python -m pytest -q
```

## Web UI
Install web extras and run development server:
```
python -m pip install -e .[web]
uvicorn pohualli.webapp:app --reload
```
Open http://127.0.0.1:8000 in a browser.

## Documentation

Published docs (main branch): https://muscariello.github.io/pohualli-python/


## Docker

Build locally:

```bash
docker build -t pohualli .
docker run --rm -p 8000:8000 pohualli
```

### Pre-built Images (GitHub Container Registry)

Multi-architecture images (linux/amd64, linux/arm64) are published automatically from `main` and version tags via GitHub Actions.

Pull latest:

```bash
docker pull ghcr.io/muscariello/pohualli-python:latest
```

Run:

```bash
docker run --rm -p 8000:8000 ghcr.io/muscariello/pohualli-python:latest
```

Use a specific version tag:

```bash
docker pull ghcr.io/muscariello/pohualli-python:v1.2.3
```

## References

* Sołtysiak, Arkadiusz & Lebeuf, Arnold. (2011). Pohualli 1.01. A computer simulation of Mesoamerican calendar systems. 8(49), 165–168.
