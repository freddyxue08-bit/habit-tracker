# Habit Tracker

Track daily habits, build streaks, and see the last 13 weeks as a GitHub-style heatmap.
Built with FastAPI, SQLModel/SQLite and plain HTML, CSS and JavaScript.

## Features
- Add, check off and delete habits, each with its own colour
- Current and longest streak per habit (a streak survives until you miss a full day)
- 13-week heatmap of check-ins
- REST API with interactive docs at `/docs`
- 19 pytest tests

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

## Test

```bash
pytest -v
```

## API

| Method | Path | What it does |
|---|---|---|
| GET | `/habits?today=YYYY-MM-DD` | List habits with streaks and recent check-ins |
| POST | `/habits` | Create a habit `{"name": "...", "color": "#hex"}` |
| GET | `/habits/{id}` | Get one habit |
| DELETE | `/habits/{id}` | Delete a habit and its check-ins |
| POST | `/habits/{id}/checkin?day=YYYY-MM-DD` | Check in (defaults to today; 409 if already done) |
| DELETE | `/habits/{id}/checkin/{day}` | Undo a check-in |

## Project layout

```
app/
  main.py      API routes + serves the frontend
  models.py    database tables and request/response shapes
  database.py  SQLite connection
  streaks.py   streak calculations
static/        frontend (index.html, style.css, app.js)
tests/         pytest tests
render.yaml    deploy config for Render
```

## Deploy (Render, free)

1. Push this repo to GitHub.
2. On render.com: **New → Blueprint**, pick this repo, click **Apply**.
3. Open the URL Render gives you.

Note: Render's free plan has no persistent disk, so the SQLite data resets
whenever the service restarts. For permanent data, add a Postgres database
and set the `DATABASE_URL` environment variable.
