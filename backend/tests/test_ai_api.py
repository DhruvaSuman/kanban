from fastapi.testclient import TestClient

from main import app


def test_ai_connectivity_returns_400_when_key_missing(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = TestClient(app)
    response = client.get("/api/ai/connectivity")
    assert response.status_code == 400
    assert "OPENROUTER_API_KEY" in response.json()["detail"]


def test_ai_chat_without_board_update_returns_current_board(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PM_DB_PATH", str(tmp_path / "phase9.db"))
    monkeypatch.setattr(
        "main.call_openrouter_structured",
        lambda board, question, conversation_history: {
            "assistant_message": "No board change needed.",
            "board_update": None,
        },
    )
    client = TestClient(app)
    response = client.post(
        "/api/ai/chat/user",
        json={"question": "What should I do next?", "conversation_history": []},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_message"] == "No board change needed."
    assert payload["board_updated"] is False
    assert "columns" in payload["board"]


def test_ai_chat_with_board_update_persists_board(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PM_DB_PATH", str(tmp_path / "phase9.db"))
    updated_board = {
        "columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]}],
        "cards": {
            "card-1": {"id": "card-1", "title": "New task", "details": "Added by AI"}
        },
    }
    monkeypatch.setattr(
        "main.call_openrouter_structured",
        lambda board, question, conversation_history: {
            "assistant_message": "I added one card.",
            "board_update": updated_board,
        },
    )
    client = TestClient(app)
    response = client.post(
        "/api/ai/chat/user",
        json={"question": "Add a task", "conversation_history": []},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["board_updated"] is True
    assert payload["board"] == updated_board

    get_response = client.get("/api/board/user")
    assert get_response.status_code == 200
    assert get_response.json() == updated_board
