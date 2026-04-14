import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from db import DEFAULT_DB_PATH, get_board_for_user, upsert_board_for_user

app = FastAPI(title="pm-mvp-backend")

STATIC_DIR = Path(__file__).parent / "static"
HELLO_FILE = STATIC_DIR / "index.html"
FRONTEND_STATIC_DIR = STATIC_DIR / "frontend"
FRONTEND_INDEX_FILE = FRONTEND_STATIC_DIR / "index.html"

DEFAULT_BOARD = {
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


@app.get("/api/board/{username}", response_model=BoardData)
def read_board(username: str) -> BoardData:
    board = get_board_for_user(username, get_db_path())
    if board is None:
        board = DEFAULT_BOARD
        upsert_board_for_user(username, board, get_db_path())
    return BoardData.model_validate(board)


@app.put("/api/board/{username}", response_model=BoardData)
def update_board(username: str, board: BoardData) -> BoardData:
    board_payload = board.model_dump()
    upsert_board_for_user(username, board_payload, get_db_path())
    return board


@app.get("/", include_in_schema=False)
def read_root() -> FileResponse:
    return serve_frontend_or_hello("")


@app.get("/{full_path:path}", include_in_schema=False)
def read_frontend_path(full_path: str) -> FileResponse:
    return serve_frontend_or_hello(full_path)
