# Pohualli (Python Port)

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
py/
  pohualli/
    composite.py        # High-level conversion + config save/load
    cli.py              # CLI with JSON output & config management
    __init__.py
    maya.py
    aztec.py
    cycle819.py
    planets.py
    yearbear.py
  tests/
    test_maya.py
    test_cycle_planets.py
    test_yearbear_cli.py
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
