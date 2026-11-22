from datetime import date, timedelta

from app.streaks import current_streak, longest_streak

TODAY = date(2026, 11, 17)


def days_ago(*offsets: int) -> set[date]:
    return {TODAY - timedelta(days=n) for n in offsets}


def test_no_checkins():
    assert current_streak(set(), TODAY) == 0
    assert longest_streak(set()) == 0


def test_streak_including_today():
    assert current_streak(days_ago(0, 1, 2), TODAY) == 3


def test_today_not_done_yet_keeps_yesterdays_streak():
    assert current_streak(days_ago(1, 2, 3), TODAY) == 3


def test_missed_yesterday_breaks_streak():
    assert current_streak(days_ago(2, 3, 4), TODAY) == 0


def test_gap_resets_current_but_not_longest():
    days = days_ago(0, 1, 5, 6, 7, 8)
    assert current_streak(days, TODAY) == 2
    assert longest_streak(days) == 4


def test_streak_across_month_boundary():
    days = {date(2026, 10, 30), date(2026, 10, 31), date(2026, 11, 1)}
    assert current_streak(days, date(2026, 11, 1)) == 3
