import os
import json
from typing import Any

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-120b"


class OpenRouterError(Exception):
    pass


def build_chat_payload(question: str) -> dict[str, Any]:
    return {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a concise assistant. Return direct answers.",
            },
            {"role": "user", "content": question},
        ],
        "temperature": 0,
    }


def build_structured_chat_payload(
    board: dict[str, Any], question: str, conversation_history: list[dict[str, str]]
) -> dict[str, Any]:
    response_schema = {
        "name": "kanban_assistant_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "assistant_message": {"type": "string"},
                "board_update": {
                    "anyOf": [
                        {"type": "null"},
                        {
                            "type": "object",
                            "properties": {
                                "columns": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "cardIds": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                        },
                                        "required": ["id", "title", "cardIds"],
                                        "additionalProperties": False,
                                    },
                                },
                                "cards": {
                                    "type": "object",
                                    "additionalProperties": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "details": {"type": "string"},
                                        },
                                        "required": ["id", "title", "details"],
                                        "additionalProperties": False,
                                    },
                                },
                            },
                            "required": ["columns", "cards"],
                            "additionalProperties": False,
                        },
                    ]
                },
            },
            "required": ["assistant_message", "board_update"],
            "additionalProperties": False,
        },
    }

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are a project management assistant. "
                "Always reply using the required JSON schema."
            ),
        },
        {
            "role": "user",
            "content": (
                "Current board JSON:\n"
                f"{json.dumps(board)}\n\n"
                "Conversation history JSON:\n"
                f"{json.dumps(conversation_history)}\n\n"
                "User question:\n"
                f"{question}"
            ),
        },
    ]

    return {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0,
        "response_format": {"type": "json_schema", "json_schema": response_schema},
    }


def parse_structured_response(raw_content: str) -> dict[str, Any]:
    cleaned_content = raw_content.strip()
    if cleaned_content.startswith("```"):
        cleaned_content = cleaned_content.strip("`")
        if cleaned_content.startswith("json"):
            cleaned_content = cleaned_content[4:].strip()
    try:
        parsed = json.loads(cleaned_content)
    except json.JSONDecodeError as error:
        raise OpenRouterError("OpenRouter structured response was not valid JSON.") from error
    if not isinstance(parsed, dict):
        raise OpenRouterError("OpenRouter structured response must be an object.")
    return parsed


def get_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise OpenRouterError("OPENROUTER_API_KEY is not configured.")
    return api_key


def call_openrouter(question: str, timeout_seconds: float = 30.0) -> str:
    payload = build_chat_payload(question)
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    response = httpx.post(
        OPENROUTER_URL, json=payload, headers=headers, timeout=timeout_seconds
    )
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise OpenRouterError("OpenRouter response missing choices.")

    message_content = choices[0].get("message", {}).get("content", "")
    if not message_content:
        raise OpenRouterError("OpenRouter response missing message content.")
    return message_content.strip()


def call_openrouter_structured(
    board: dict[str, Any],
    question: str,
    conversation_history: list[dict[str, str]],
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    payload = build_structured_chat_payload(board, question, conversation_history)
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    response = httpx.post(
        OPENROUTER_URL, json=payload, headers=headers, timeout=timeout_seconds
    )
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise OpenRouterError("OpenRouter response missing choices.")
    message_content = choices[0].get("message", {}).get("content", "")
    if not message_content:
        raise OpenRouterError("OpenRouter response missing message content.")
    return parse_structured_response(message_content)
