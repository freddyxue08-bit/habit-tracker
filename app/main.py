from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, delete, select

from .database import create_db_and_tables, get_session
from .models import CheckIn, Habit, HabitCreate, HabitRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()  # runs once when the server starts
    yield


app = FastAPI(title="Habit Tracker", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Habit Tracker API. Visit /docs to try it out."}


# --- Milestone 1: habit CRUD ------------------------------------------------

@app.get("/habits", response_model=list[HabitRead])
def list_habits(session: Session = Depends(get_session)):
    return session.exec(select(Habit).order_by(Habit.created_at)).all()


@app.post("/habits", response_model=HabitRead, status_code=201)
def create_habit(habit: HabitCreate, session: Session = Depends(get_session)):
    db_habit = Habit.model_validate(habit)
    session.add(db_habit)
    session.commit()
    session.refresh(db_habit)  # reload so id and created_at are filled in
    return db_habit


@app.get("/habits/{habit_id}", response_model=HabitRead)
def get_habit(habit_id: int, session: Session = Depends(get_session)):
    habit = session.get(Habit, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@app.delete("/habits/{habit_id}", status_code=204)
def delete_habit(habit_id: int, session: Session = Depends(get_session)):
    habit = session.get(Habit, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    session.exec(delete(CheckIn).where(CheckIn.habit_id == habit_id))
    session.delete(habit)
    session.commit()


# --- Milestone 2 (your turn!) -----------------------------------------------
# TODO: POST   /habits/{habit_id}/checkin         -> mark today as done
# TODO: DELETE /habits/{habit_id}/checkin/{day}   -> undo a check-in
# Hint: the UniqueConstraint on CheckIn raises sqlalchemy.exc.IntegrityError
#       if you check in twice on the same day. Catch it and return 409.
