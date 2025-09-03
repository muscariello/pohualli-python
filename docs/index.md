# Pohualli Python

Pohualli is a Python port of a classic Turbo Pascal calendrical tool focused on Mesoamerican systems (Maya & Aztec).

## Features

- Tzolk'in (Tzolkin) and Haab conversions
- Long Count computation
- Year bearer derivation
- 819-day station & directional color determination
- Planetary synodic indices
- Moon age / eclipse possibility heuristics
- Zodiac degrees & names
- Configurable correction offsets & new era
- JSON composite API & FastAPI web UI

## Install

```bash
pip install -e .[web]
```

Or just core:

```bash
pip install -e .
```

## Quick Example

```python
from pohualli import compute_composite
res = compute_composite(2451545)
print(res.tzolkin_value, res.tzolkin_name, res.long_count)
```

## Next Steps

- Read the Quick Start for end-to-end examples.
- Explore Concepts for calendar background.
- See Python API for data structures.
