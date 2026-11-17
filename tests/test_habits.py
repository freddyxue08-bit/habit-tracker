# The `client` fixture lives in conftest.py.


def test_create_and_list_habits(client):
    res = client.post("/habits", json={"name": "Read 20 pages"})
    assert res.status_code == 201
    habit = res.json()
    assert habit["name"] == "Read 20 pages"
    assert habit["id"] is not None

    res = client.get("/habits")
    assert [h["name"] for h in res.json()] == ["Read 20 pages"]


def test_empty_name_is_rejected(client):
    res = client.post("/habits", json={"name": ""})
    assert res.status_code == 422


def test_get_missing_habit_returns_404(client):
    assert client.get("/habits/999").status_code == 404


def test_delete_habit(client):
    habit_id = client.post("/habits", json={"name": "Gym"}).json()["id"]
    assert client.delete(f"/habits/{habit_id}").status_code == 204
    assert client.get(f"/habits/{habit_id}").status_code == 404
    

def test_client_cannot_choose_id(client):
    res = client.post("/habits", json={"name": "Gym", "id": 99})
    assert res.status_code == 201
    assert res.json()["id"] != 99


def test_default_color(client):
    res = client.post("/habits", json={"name": "Meditate"})
    assert res.status_code == 201
    assert res.json()["color"] == "#22c55e"

