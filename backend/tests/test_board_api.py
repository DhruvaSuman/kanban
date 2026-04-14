from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_get_board_seeds_default_when_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PM_DB_PATH", str(tmp_path / "phase6.db"))
    client = TestClient(app)

    response = client.get("/api/board/user")
    assert response.status_code == 200
    payload = response.json()
    assert "columns" in payload
    assert "cards" in payload
    assert len(payload["columns"]) == 5


def test_put_then_get_board_round_trip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PM_DB_PATH", str(tmp_path / "phase6.db"))
    client = TestClient(app)
    board_payload = {
        "columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]}],
        "cards": {
            "card-1": {"id": "card-1", "title": "Build API", "details": "Phase 6 task"}
        },
    }

    put_response = client.put("/api/board/user", json=board_payload)
    assert put_response.status_code == 200
    assert put_response.json() == board_payload

    get_response = client.get("/api/board/user")
    assert get_response.status_code == 200
    assert get_response.json() == board_payload


def test_db_is_created_during_api_request(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "nested" / "api.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))
    client = TestClient(app)
    assert not db_path.exists()

    response = client.get("/api/board/user")
    assert response.status_code == 200
    assert db_path.exists()
