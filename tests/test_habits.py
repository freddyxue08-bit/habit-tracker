import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture
def client():
    # A fresh in-memory database for every test, so tests never touch habits.db.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


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

