# Habit Tracker

Track daily habits and build streaks. Built with FastAPI + SQLite.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs to try the endpoints.

## Run the tests

```bash
pytest
```

## Roadmap

- [x] Milestone 1: habit CRUD API
- [ ] Milestone 2: daily check-ins
- [ ] Milestone 3: streak calculation + tests
- [ ] Milestone 4: frontend
- [ ] Milestone 5: calendar heatmap
- [ ] Milestone 6: deploy
