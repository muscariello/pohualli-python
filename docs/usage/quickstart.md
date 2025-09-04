# Quick Start

This guide shows the fastest way to explore Pohualli.

## 1. Install

Choose one:

PyPI (CLI & library):
```bash
pip install pohualli
```
With web UI extras:
```bash
pip install "pohualli[web]"
```
Desktop App (macOS / Windows): download bundle artifact from a Release (no Python needed). First macOS run: Control-click → Open.
From source (dev):
```bash
pip install -e .[dev,web,docs]
```

## 2. CLI

```bash
pohualli from-jdn 2451545 --json
```

## 3. Python

```python
from pohualli import compute_composite
print(compute_composite(2451545).tzolkin_name)
```

## 4. Web UI

```bash
uvicorn pohualli.webapp:app --reload
# open http://127.0.0.1:8000
```

## 5. Configuration

Adjust New Era or year bearer reference via query params or CLI flags.
