# SmartNest Rental — Flask application

Structured Flask app for the SmartNest rental platform. It serves the UI from `../client` and reuses ML logic from `../server/util.py`.

## Project layout

```
flask/
  app/
    __init__.py      # application factory
    config.py        # settings
    ml.py            # loads ../server/util.py
    api/routes.py    # /api/* endpoints
    web/routes.py    # UI static files
  run.py             # development server
  wsgi.py            # production (gunicorn)
  requirements.txt
```

## Setup

```powershell
cd d:\smartnest.ai\smartnest_rental_platform\flask
python -m pip install -r requirements.txt
```

Ensure `../model/artifacts` exists (train models first if needed).

## Run (development)

```powershell
python run.py
```

Open **http://127.0.0.1:8000/**

## Run (production)

```powershell
gunicorn -w 1 -k gthread --threads 4 -b 0.0.0.0:8000 wsgi:app
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | HTTP port |
| `HOST` | `0.0.0.0` | Bind address |
| `FLASK_DEBUG` | `0` | `1` enables debug mode |
| `EAGER_LOAD_ARTIFACTS` | `1` | Load ML models at startup |
