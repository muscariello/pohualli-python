# Development

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,web,docs]
```

## Tests

```bash
pytest -q
```

## Docs Live Preview

```bash
mkdocs serve
```

Open http://127.0.0.1:8000 (web UI) or http://127.0.0.1:8001 (if mkdocs shows different port in output).
