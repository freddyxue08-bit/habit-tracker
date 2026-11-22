from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, delete, select

from .database import create_db_and_tables, get_session
from .models import CheckIn, CheckInRead, Habit, HabitCreate, HabitRead, HabitWithStats
from .streaks import current_streak, longest_streak

HEATMAP_DAYS = 91  # 13 weeks
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()  # runs once when the server starts
    yield


app = FastAPI(title="Habit Tracker", lifespan=lifespan)


def get_habit_or_404(session: Session, habit_id: int) -> Habit:
    habit = session.get(Habit, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


# --- Habits -----------------------------------------------------------------

@app.get("/habits", response_model=list[HabitWithStats])
def list_habits(today: date | None = None, session: Session = Depends(get_session)):
    # The browser sends its own "today" so streaks follow the user's timezone.
    today = today or date.today()
    habits = session.exec(select(Habit).order_by(Habit.created_at)).all()

    # One query for all check-ins, then group them by habit in Python.
    days_by_habit: dict[int, set[date]] = {}
    for checkin in session.exec(select(CheckIn)).all():
        days_by_habit.setdefault(checkin.habit_id, set()).add(checkin.day)

    window_start = today - timedelta(days=HEATMAP_DAYS - 1)
    result = []
    for habit in habits:
        days = days_by_habit.get(habit.id, set())
        result.append(
            HabitWithStats(
                **habit.model_dump(),
                current_streak=current_streak(days, today),
                longest_streak=longest_streak(days),
                done_today=today in days,
                recent_days=sorted(d for d in days if window_start <= d <= today),
            )
        )
    return result


@app.post("/habits", response_model=HabitRead, status_code=201)
def create_habit(habit: HabitCreate, session: Session = Depends(get_session)):
    db_habit = Habit.model_validate(habit)
    session.add(db_habit)
    session.commit()
    session.refresh(db_habit)  # reload so id and created_at are filled in
    return db_habit


@app.get("/habits/{habit_id}", response_model=HabitRead)
def get_habit(habit_id: int, session: Session = Depends(get_session)):
    return get_habit_or_404(session, habit_id)


@app.delete("/habits/{habit_id}", status_code=204)
def delete_habit(habit_id: int, session: Session = Depends(get_session)):
    habit = get_habit_or_404(session, habit_id)
    session.exec(delete(CheckIn).where(CheckIn.habit_id == habit_id))
    session.delete(habit)
    session.commit()


# --- Check-ins --------------------------------------------------------------

@app.post("/habits/{habit_id}/checkin", response_model=CheckInRead, status_code=201)
def check_in(habit_id: int, day: date | None = None, session: Session = Depends(get_session)):
    get_habit_or_404(session, habit_id)
    day = day or date.today()
    # Allow one day of slack for timezones ahead of the server, but no further.
    if day > date.today() + timedelta(days=1):
        raise HTTPException(status_code=400, detail="Can't check in for a future day")

    checkin = CheckIn(habit_id=habit_id, day=day)
    session.add(checkin)
    try:
        session.commit()
    except IntegrityError:  # the UniqueConstraint(habit_id, day) fired
        session.rollback()
        raise HTTPException(status_code=409, detail="Already checked in for that day")
    session.refresh(checkin)
    return checkin


@app.delete("/habits/{habit_id}/checkin/{day}", status_code=204)
def undo_check_in(habit_id: int, day: date, session: Session = Depends(get_session)):
    checkin = session.exec(
        select(CheckIn).where(CheckIn.habit_id == habit_id, CheckIn.day == day)
    ).first()
    if checkin is None:
        raise HTTPException(status_code=404, detail="No check-in for that day")
    session.delete(checkin)
    session.commit()


# --- Frontend ---------------------------------------------------------------
# Mounted last so the API routes above always win. Serves static/index.html at "/".
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
