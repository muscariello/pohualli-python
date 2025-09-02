# Pohualli (Python Port)

Python port (work in progress) of the Turbo Pascal Pohualli calendrical utility (Mesoamerican / Maya & Aztec related calculations).

Authorization to access original Pascal source code provided by Arnold Lebeuf to Luca Muscariello (May 2020).

## Features Implemented

- Tzolkin & Haab date conversions
- Long Count with configurable New Era constant
- Year Bearer packed value
- 819-day cycle & direction color
- Basic planetary (Mercury & Venus) synodic calculations
- Moon age, abnormal distance, eclipse window heuristic
- Stellar & Earth zodiac degree + name mapping
- Composite calculator API
- CLI with JSON output & config persistence
- FastAPI web UI (HTML + JSON endpoint)

## Running Locally (without Docker)

```bash
cd py
python -m venv .venv
. .venv/bin/activate
pip install -e .[web]
uvicorn pohualli.webapp:app --reload --port 8000
```
Then open: http://127.0.0.1:8000

## Docker

Build image:
```bash
docker build -t pohualli .
```

Run container:
```bash
docker run --rm -p 8000:8000 pohualli
```

Or with docker compose:
```bash
docker compose up --build
```

Open http://localhost:8000 to use the UI.

## CLI Usage

After installing (editable or via image shell):
```bash
pohualli from-jdn 2451545 --json
```

## Tests

```bash
cd py
pytest -q
```

## Roadmap / Next Steps

- Additional planetary bodies
- Full corrections model & validation dataset
- Internationalization / localization in UI
- Dark mode & accessibility pass
- Container healthcheck & production-ready image refinements

## License

MIT (port); original Pascal code under permission from author.

