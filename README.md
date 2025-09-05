# Pohualli (Python Port)

[![CI](https://github.com/muscariello/pohualli-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/muscariello/pohualli-python/actions/workflows/ci.yml) [![Coverage](https://codecov.io/gh/muscariello/pohualli-python/branch/main/graph/badge.svg)](https://codecov.io/gh/muscariello/pohualli-python) [![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://muscariello.github.io/pohualli-python/) [![PyPI](https://img.shields.io/pypi/v/pohualli.svg)](https://pypi.org/project/pohualli/) [![Changelog](https://img.shields.io/badge/changelog-latest-orange)](CHANGELOG.md)

Python reimplementation of the original Turbo Pascal Pohualli calendrical utility.

## Highlights

- Maya & Aztec core calculations (Tzolk'in, Haab, Long Count, Year Bearer)
- 819‑day cycle, planetary synodic helpers, zodiac & moon heuristics
- Correlation ("New Era") presets + on-the-fly overrides
- Auto-derivation of correction offsets from partial constraints
- Unified composite API & high-coverage test suite (≥90% per file)
- FastAPI web UI + CLI + JSON output

## Install

### Option 1: PyPI (CLI & library)
```
pip install pohualli
```
Include web extras (FastAPI UI) if you want the local server:
```
pip install "pohualli[web]"
```
PyPI: https://pypi.org/project/pohualli/

### Option 2: Desktop Bundle (macOS / Windows)
Download the pre-built bundle artifacts (App on macOS, MSI or app dir on Windows) from the Desktop Bundles workflow or a Release.

macOS first run (unsigned / ad‑hoc bundle):
1. Move `Pohualli.app` to `/Applications` (optional but typical).
2. Control‑click the app → Open → Open (this whitelists it in Gatekeeper).
3. Browser opens automatically; if not, visit the printed `http://127.0.0.1:<port>`.

Windows:
1. Run the MSI or `Pohualli.exe` inside the unpacked directory.
2. If SmartScreen warns, choose “More info” → “Run anyway”.
3. Browser tab should appear automatically.

Updates: replace the old bundle with the new one (no persistent user data yet).

Latest release downloads: https://github.com/muscariello/pohualli-python/releases

### Option 3: From Source (development)
```
git clone https://github.com/muscariello/pohualli-python.git
cd pohualli-python
pip install -e .[dev,web]
```
Then run CLI (`pohualli ...`) or web app (`uvicorn pohualli.webapp:app --reload`).

## Structure
```
.
├── CHANGELOG.md                     # Project changelog / release notes
├── LICENSE                          # GPL-3.0-only license text
├── README.md                        # Overview & usage (this file)
├── docker-compose.yml               # Convenience orchestration for web app
├── Dockerfile                       # Multi-arch container build definition
├── mkdocs.yml                       # MkDocs Material documentation config
├── pyproject.toml                   # Packaging & dependency metadata
├── docs/                            # Documentation markdown sources (MkDocs)
│   ├── index.md                     # Landing page
│   ├── dev.md                       # Development & contributing notes
│   ├── license.md                   # License blurb for docs site
│   ├── concepts/                    # Conceptual explanations
│   │   ├── calendars.md             # Calendar systems overview
│   │   └── configuration.md         # Correlations & correction parameters
│   └── usage/                       # How-to guides
│       ├── quickstart.md            # Quick installation & first run
│       ├── cli.md                   # CLI usage details
│       ├── desktop.md               # Desktop bundles (Briefcase) guide
│       └── python-api.md            # Python API examples
├── pohualli/
│   ├── __init__.py                  # Public API exports (compute_composite, etc.)
│   ├── __main__.py                  # Module entry point (python -m pohualli / bundle)
│   ├── autocorr.py                  # Derive correction offsets from constraints
│   ├── aztec.py                     # Aztec (Tonalpohualli) name tables & helpers
│   ├── calendar_dates.py            # Gregorian/Julian conversions & weekday calc
│   ├── cli.py                       # Command line interface entry point
│   ├── composite.py                 # High-level composite computation orchestrator
│   ├── correlations.py              # Correlation (New Era) preset definitions
│   ├── cycle819.py                  # 819‑day cycle station & direction colors
│   ├── desktop_app.py               # Desktop launcher for packaged app (Briefcase)
│   ├── maya.py                      # Core Maya calendar math (Tzolk'in / Haab / LC)
│   ├── moon.py                      # Moon phase / anomaly heuristics
│   ├── planets.py                   # Planetary synodic value helpers
│   ├── templates/
│   │   └── index.html               # Web UI Jinja2 template
│   ├── types.py                     # Dataclasses & global correction state types
│   ├── webapp.py                    # FastAPI application (async range jobs, endpoints)
│   ├── yearbear.py                  # Year Bearer packing/unpacking utilities
│   └── zodiac.py                    # Star & earth zodiac angle computations
└── tests/                           # Pytest suite (broad branch coverage)
  ├── test_async_range_job.py          # Async range job creation & polling
  ├── test_async_cancel_partial.py     # Cancellation partial-results semantics
  ├── test_autocorr*.py                # Auto-correction derivation & edge cases
  ├── test_cli_direct.py               # Direct main() invocation basic paths
  ├── test_cli_early_filters_paths.py  # Early filter continue branches (range)
  ├── test_cli_more.py                 # JSON output & new-era/year bearer refs
  ├── test_cli_no_subproc.py           # CLI coverage without subprocess fork
  ├── test_cli_range_matrix.py         # Combinatorial filter matrix (range)
  ├── test_cli_search_range*.py        # Range search modes (table/json-lines)
  ├── test_cli_textual_branches.py     # Textual from-jdn output branches
  ├── test_composite.py                # Composite object field consistency
  ├── test_cycle_planets.py            # 819-cycle & planetary helpers
  ├── test_desktop_app.py              # Desktop launcher behavior
  ├── test_extra_cycles_yearbear_moon.py # Mixed composite cycle branches
  ├── test_maya*.py                    # Maya calendar arithmetic & validation
  ├── test_moon_zodiac.py              # Moon + zodiac computations
  ├── test_web.py                      # Basic web endpoint checks
  ├── test_web_extra.py                # Additional /api/convert / derive cases
  ├── test_web_range_job_extra.py      # Range job edge cases & listing
  ├── test_webapp_internal.py          # Internal helpers (_early_filters etc.)
  ├── test_webapp_filters_matrix.py    # Each filter type in async jobs
  ├── test_webapp_more.py              # Not-found, cancel-after-complete, culture
  ├── test_webapp_additional.py        # Reversed ranges, invalid specs, limits
  ├── test_yearbear_cli.py             # Year bearer & CLI integration
  └── test_zodiac_extra.py             # Additional zodiac heuristic coverage
```

## Python Usage
```python
from pohualli import compute_composite
result = compute_composite(2451545)
print(result.tzolkin_name, result.long_count, result.star_zodiac_name)
```

## CLI Examples
```
# Basic human-readable conversion
pohualli from-jdn 2451545

# Year Bearer reference override
pohualli from-jdn 2451545 --year-bearer-ref 0 0

# JSON output (pretty with jq)
pohualli from-jdn 2451545 --json | jq .long_count

# Override New Era just for this invocation
pohualli from-jdn 2451545 --new-era 584283 --json

# Apply a named correlation preset globally
pohualli apply-correlation gmt-584283

# List available correlations
pohualli list-correlations

# Derive corrections from partial constraint (tzolkin only)
pohualli derive-autocorr 2451545 --tzolkin "4 Ahau"

# Derive with multiple constraints (tzolkin + haab + g)
pohualli derive-autocorr 2451545 --tzolkin "4 Ahau" --haab "3 Pop" --g 5

# Persist and restore configuration
pohualli save-config config.json
pohualli load-config config.json

# Full JSON composite into a file
pohualli from-jdn 2451545 --json > composite.json

# Range search (scan inclusive JDN interval with filters)
# Find first 5 dates in a span whose Tzolkin name is Imix and Haab month is Cumhu
pohualli search-range 584283 584500 --tzolkin-name Imix --haab-month Cumhu --limit 5

# Long Count pattern matching (use * as wildcard for a component)
pohualli search-range 500000 600000 --long-count '9.*.*.*.*.*' --limit 3

# Output JSON lines (machine processing)
pohualli search-range 584283 584400 --tzolkin-value 4 --json-lines --limit 2

# Select custom output fields
pohualli search-range 584283 584400 --fields jdn,tzolkin_name,haab_month_name --limit 3

# Switch to Aztec year-bearer derivation (subtracts 364 days in interval logic)
pohualli from-jdn 2451545 --culture aztec --year-bearer-ref 0 0

# Range search in Aztec mode
pohualli search-range 584283 584400 --culture aztec --tzolkin-value 4 --limit 2
```

## Web App
```
uvicorn pohualli.webapp:app --reload
```
Open http://127.0.0.1:8000

## Docker
```
docker build -t pohualli .
docker run --rm -p 8000:8000 pohualli
```
Or use the published image:
```
docker run --rm -p 8000:8000 ghcr.io/muscariello/pohualli-python:latest
```

## Testing
```
pytest -q
```

## License
GPL-3.0-only

### Maya vs Aztec Year Bearer Note
The computation of the Year Bearer differs: in Aztec (tonalpohualli) mode the interval between the target Haab position and the reference is reduced by 364 days before deriving the bearer, shifting the resulting Tzolkin pair relative to Maya convention. Use `--culture aztec` (CLI) or the Culture dropdown in the web UI to toggle. Default is Maya.

## Reference
Sołtysiak, A. & Lebeuf, A. (2011). Pohualli 1.01. A computer simulation of Mesoamerican calendar systems. 8(49), 165–168. [ResearchGate](https://www.researchgate.net/publication/270956742_2011_Pohualli_101_A_computer_simulation_of_Mesoamerican_calendar_systems)
