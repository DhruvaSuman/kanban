import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ai import (
    OpenRouterError,
    OPENROUTER_MODEL,
    call_openrouter,
    call_openrouter_structured,
)
from db import DEFAULT_DB_PATH, get_board_for_user, upsert_board_for_user

app = FastAPI(title="pm-mvp-backend")

STATIC_DIR = Path(__file__).parent / "static"
HELLO_FILE = STATIC_DIR / "index.html"
FRONTEND_STATIC_DIR = STATIC_DIR / "frontend"
FRONTEND_INDEX_FILE = FRONTEND_STATIC_DIR / "index.html"

SEEDED_USER_BOARD = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Gather customer signals",
            "details": "Review support tags, sales notes, and churn feedback.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototype analytics view",
            "details": "Sketch initial dashboard layout and key drill-downs.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refine status language",
            "details": "Standardize column labels and tone across the board.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Design card layout",
            "details": "Add hierarchy and spacing for scanning dense lists.",
        },
        "card-6": {
            "id": "card-6",
            "title": "QA micro-interactions",
            "details": "Verify hover, focus, and loading states.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Ship marketing page",
            "details": "Final copy approved and asset pack delivered.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Close onboarding sprint",
            "details": "Document release notes and share internally.",
        },
    },
}

EMPTY_BOARD = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": []},
        {"id": "col-discovery", "title": "Discovery", "cardIds": []},
        {"id": "col-progress", "title": "In Progress", "cardIds": []},
        {"id": "col-review", "title": "Review", "cardIds": []},
        {"id": "col-done", "title": "Done", "cardIds": []},
    ],
    "cards": {},
}


class Card(BaseModel):
    id: str
    title: str
    details: str


class Column(BaseModel):
    id: str
    title: str
    cardIds: list[str]


class BoardData(BaseModel):
    columns: list[Column]
    cards: dict[str, Card]


class AIConnectivityResult(BaseModel):
    model: str
    question: str
    answer: str


class ChatMessage(BaseModel):
    role: str
    content: str


class AIChatRequest(BaseModel):
    question: str
    conversation_history: list[ChatMessage] = Field(default_factory=list)


class AIStructuredOutput(BaseModel):
    assistant_message: str
    board_update: BoardData | None = None


class AIChatResponse(BaseModel):
    assistant_message: str
    board: BoardData
    board_updated: bool


def get_db_path() -> Path:
    configured_path = os.getenv("PM_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return DEFAULT_DB_PATH


def serve_frontend_or_hello(path: str) -> FileResponse:
    requested_path = path.strip("/")
    requested_file = FRONTEND_STATIC_DIR / requested_path
    if requested_path and requested_file.exists() and requested_file.is_file():
        return FileResponse(requested_file)
    if FRONTEND_INDEX_FILE.exists():
        return FileResponse(FRONTEND_INDEX_FILE)
    return FileResponse(HELLO_FILE)


@app.get("/api/health")
def read_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hello")
def read_hello() -> dict[str, str]:
    return {"message": "hello from fastapi"}


@app.get("/api/ai/connectivity", response_model=AIConnectivityResult)
def read_ai_connectivity() -> AIConnectivityResult:
    question = "What is 2+2? Reply with only the final answer."
    try:
        answer = call_openrouter(question)
    except OpenRouterError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"OpenRouter call failed: {error}") from error

    return AIConnectivityResult(
        model=OPENROUTER_MODEL,
        question=question,
        answer=answer,
    )


@app.get("/api/board/{username}", response_model=BoardData)
def read_board(username: str) -> BoardData:
    board = get_board_for_user(username, get_db_path())
    if board is None:
        board = SEEDED_USER_BOARD if username == "user" else EMPTY_BOARD
        upsert_board_for_user(username, board, get_db_path())
    return BoardData.model_validate(board)


@app.put("/api/board/{username}", response_model=BoardData)
def update_board(username: str, board: BoardData) -> BoardData:
    board_payload = board.model_dump()
    upsert_board_for_user(username, board_payload, get_db_path())
    return board


@app.post("/api/ai/chat/{username}", response_model=AIChatResponse)
def chat_with_ai(username: str, payload: AIChatRequest) -> AIChatResponse:
    current_board = read_board(username)
    conversation_history = [
        {"role": message.role, "content": message.content}
        for message in payload.conversation_history
    ]

    try:
        ai_raw_response = call_openrouter_structured(
            board=current_board.model_dump(),
            question=payload.question,
            conversation_history=conversation_history,
        )
    except OpenRouterError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"OpenRouter call failed: {error}") from error

    structured = AIStructuredOutput.model_validate(ai_raw_response)
    if structured.board_update:
        upsert_board_for_user(username, structured.board_update.model_dump(), get_db_path())
        return AIChatResponse(
            assistant_message=structured.assistant_message,
            board=structured.board_update,
            board_updated=True,
        )

    return AIChatResponse(
        assistant_message=structured.assistant_message,
        board=current_board,
        board_updated=False,
    )


@app.get("/", include_in_schema=False)
def read_root() -> FileResponse:
    return serve_frontend_or_hello("")


@app.get("/{full_path:path}", include_in_schema=False)
def read_frontend_path(full_path: str) -> FileResponse:
    return serve_frontend_or_hello(full_path)
