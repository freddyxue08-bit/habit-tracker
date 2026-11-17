from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint


# --- Habits -----------------------------------------------------------------

class HabitBase(SQLModel):
    """Fields shared by every Habit shape."""
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(default="#22c55e", max_length=7)  # hex colour for the UI


class Habit(HabitBase, table=True):
    """The database table."""
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HabitCreate(HabitBase):
    """What the client sends when creating a habit (validated)."""


class HabitRead(HabitBase):
    """What the API sends back."""
    id: int
    created_at: datetime


class HabitWithStats(HabitRead):
    """A habit plus everything the frontend needs to draw its card."""
    current_streak: int
    longest_streak: int
    done_today: bool
    recent_days: list[date]  # check-ins in the heatmap window


# --- Check-ins --------------------------------------------------------------

class CheckIn(SQLModel, table=True):
    """One row per habit per day it was completed."""
    __table_args__ = (UniqueConstraint("habit_id", "day"),)

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habit.id", index=True)
    day: date


class CheckInRead(SQLModel):
    id: int
    habit_id: int
    day: date
