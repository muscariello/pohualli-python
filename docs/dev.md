# Development

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,docs]
```

## Tests

```bash
pytest -q
```

## Docs Live Preview

```bash
mkdocs serve
```

Open the URL printed by MkDocs (typically http://127.0.0.1:8000).
