from datetime import date, timedelta

ONE_DAY = timedelta(days=1)


def current_streak(days: set[date], today: date) -> int:
    """Consecutive days ending today.

    If today isn't checked yet, count back from yesterday instead, so the
    streak doesn't "break" in the morning before you've done the habit.
    """
    day = today if today in days else today - ONE_DAY
    streak = 0
    while day in days:
        streak += 1
        day -= ONE_DAY
    return streak


def longest_streak(days: set[date]) -> int:
    """Longest run of consecutive days ever."""
    best = 0
    for day in days:
        if day - ONE_DAY in days:
            continue  # not the start of a run, skip it
        length = 1
        while day + ONE_DAY * length in days:
            length += 1
        best = max(best, length)
    return best
