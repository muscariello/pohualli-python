# Pohualli (Python Port)

[![CI](https://github.com/muscariello/pohualli-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/muscariello/pohualli-python/actions/workflows/ci.yml) [![Coverage](https://codecov.io/gh/muscariello/pohualli-python/branch/main/graph/badge.svg)](https://codecov.io/gh/muscariello/pohualli-python) [![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://muscariello.github.io/pohualli-python/) [![PyPI](https://img.shields.io/pypi/v/pohualli.svg)](https://pypi.org/project/pohualli/)

Python reimplementation of the original Turbo Pascal Pohualli calendrical utility.

## Highlights

- Maya and Aztec core calculations (Tzolk'in, Haab, Long Count, Year Bearer)
- 819-day cycle, planetary synodic helpers, zodiac and moon heuristics
- Correlation presets and configurable correction offsets
- CLI, Python API, and JSON-RPC backend
- Flutter desktop UI for macOS and Windows

## Install

### PyPI (CLI + library)

```bash
pip install pohualli
```

### From source (development)

```bash
git clone https://github.com/muscariello/pohualli-python.git
cd pohualli-python
pip install -e .[dev,docs]
```

## CLI Quick Examples

```bash
pohualli from-jdn 2451545 --json
pohualli search-range 584283 584400 --tzolkin-value 4 --limit 2
pohualli derive-autocorr 2451545 --tzolkin "4 Ahau"
```

## Python Quick Example

```python
from pohualli import compute_composite

result = compute_composite(2451545)
print(result.tzolkin_name, result.long_count)
```

## RPC Backend (used by Flutter)

```bash
pohualli-rpc
```

JSON-RPC methods:

- `health`
- `list_correlations`
- `convert`
- `derive_autocorr`
- `search_range`
- `quit`

## Flutter Desktop App

- Project: `flutter/pohualli_desktop`
- Workflow: `.github/workflows/flutter-desktop.yml`
- Release artifacts include a bundled self-contained backend executable (`pohualli-rpc-bin`)

Run locally:

```bash
cd flutter/pohualli_desktop
flutter pub get
flutter run -d macos
# or: flutter run -d windows
```

Build locally:

```bash
flutter build macos --release
flutter build windows --release
```

## Testing

```bash
pytest -q
```

Flutter checks:

```bash
cd flutter/pohualli_desktop
flutter analyze
flutter test --coverage
```

## Documentation

- Docs site: https://muscariello.github.io/pohualli-python/
- Desktop usage guide: `docs/usage/desktop.md`

## License

GPL-3.0-only
