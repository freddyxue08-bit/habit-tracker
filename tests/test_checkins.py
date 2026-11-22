from datetime import date, timedelta

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)


def make_habit(client, name="Gym"):
    return client.post("/habits", json={"name": name}).json()["id"]


def get_only_habit(client, today=TODAY):
    return client.get(f"/habits?today={today}").json()[0]


def test_check_in_today(client):
    habit_id = make_habit(client)
    res = client.post(f"/habits/{habit_id}/checkin")
    assert res.status_code == 201
    assert res.json()["day"] == TODAY.isoformat()

    habit = get_only_habit(client)
    assert habit["done_today"] is True
    assert habit["current_streak"] == 1


def test_double_check_in_returns_409(client):
    habit_id = make_habit(client)
    assert client.post(f"/habits/{habit_id}/checkin").status_code == 201
    assert client.post(f"/habits/{habit_id}/checkin").status_code == 409


def test_check_in_specific_day_builds_streak(client):
    habit_id = make_habit(client)
    client.post(f"/habits/{habit_id}/checkin?day={YESTERDAY}")
    client.post(f"/habits/{habit_id}/checkin?day={TODAY}")

    habit = get_only_habit(client)
    assert habit["current_streak"] == 2
    assert habit["recent_days"] == [YESTERDAY.isoformat(), TODAY.isoformat()]


def test_future_check_in_rejected(client):
    habit_id = make_habit(client)
    future = TODAY + timedelta(days=5)
    assert client.post(f"/habits/{habit_id}/checkin?day={future}").status_code == 400


def test_check_in_missing_habit_returns_404(client):
    assert client.post("/habits/999/checkin").status_code == 404


def test_undo_check_in(client):
    habit_id = make_habit(client)
    client.post(f"/habits/{habit_id}/checkin")
    assert client.delete(f"/habits/{habit_id}/checkin/{TODAY}").status_code == 204
    assert get_only_habit(client)["done_today"] is False
    # Undoing again: nothing left to delete.
    assert client.delete(f"/habits/{habit_id}/checkin/{TODAY}").status_code == 404


def test_deleting_habit_removes_its_check_ins(client):
    old_id = make_habit(client, "Old")
    client.post(f"/habits/{old_id}/checkin")
    client.delete(f"/habits/{old_id}")

    # Even if SQLite reuses the id, the new habit must start with no streak.
    make_habit(client, "New")
    habit = get_only_habit(client)
    assert habit["current_streak"] == 0
    assert habit["recent_days"] == []
