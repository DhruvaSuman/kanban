import os

import pytest

from ai import (
    OPENROUTER_MODEL,
    OpenRouterError,
    build_chat_payload,
    build_structured_chat_payload,
    call_openrouter,
    call_openrouter_structured,
    parse_structured_response,
)


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


def test_build_chat_payload_uses_required_model() -> None:
    payload = build_chat_payload("What is 2+2?")
    assert payload["model"] == OPENROUTER_MODEL
    assert payload["messages"][1]["content"] == "What is 2+2?"


def test_call_openrouter_raises_when_api_key_missing(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(OpenRouterError):
        call_openrouter("What is 2+2?")


def test_build_structured_payload_includes_board_and_history() -> None:
    payload = build_structured_chat_payload(
        board={"columns": [], "cards": {}},
        question="Move task A to review",
        conversation_history=[{"role": "user", "content": "hello"}],
    )
    assert payload["model"] == OPENROUTER_MODEL
    assert payload["response_format"]["type"] == "json_schema"
    assert "Current board JSON" in payload["messages"][1]["content"]
    assert "Conversation history JSON" in payload["messages"][1]["content"]


def test_parse_structured_response_reads_json_object() -> None:
    parsed = parse_structured_response(
        '{"assistant_message":"done","board_update":{"columns":[],"cards":{}}}'
    )
    assert parsed["assistant_message"] == "done"
    assert parsed["board_update"]["columns"] == []


def test_parse_structured_response_raises_on_invalid_json() -> None:
    with pytest.raises(OpenRouterError):
        parse_structured_response("not-json")


def test_call_openrouter_success(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "ai.httpx.post",
        lambda *args, **kwargs: DummyResponse(
            {"choices": [{"message": {"content": "4"}}]}
        ),
    )
    answer = call_openrouter("What is 2+2?")
    assert answer == "4"


def test_call_openrouter_raises_on_missing_choices(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr("ai.httpx.post", lambda *args, **kwargs: DummyResponse({}))
    with pytest.raises(OpenRouterError):
        call_openrouter("What is 2+2?")


def test_call_openrouter_structured_success(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "ai.httpx.post",
        lambda *args, **kwargs: DummyResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": '{"assistant_message":"ok","board_update":null}'
                        }
                    }
                ]
            }
        ),
    )
    result = call_openrouter_structured(
        board={"columns": [], "cards": {}},
        question="No changes",
        conversation_history=[],
    )
    assert result["assistant_message"] == "ok"
    assert result["board_update"] is None


def test_live_connectivity_2_plus_2_if_key_present() -> None:
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set; skipping live connectivity test.")

    answer = call_openrouter("What is 2+2? Reply with only the final answer.")
    normalized_answer = answer.strip().lower()
    assert "4" in normalized_answer
