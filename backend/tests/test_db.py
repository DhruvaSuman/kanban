import sqlite3
from pathlib import Path

from db import get_board_for_user, init_db, upsert_board_for_user


def test_init_db_creates_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    init_db(db_path)

    with sqlite3.connect(db_path) as connection:
        table_rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()
    tables = {row[0] for row in table_rows}
    assert "users" in tables
    assert "boards" in tables


def test_upsert_and_read_board_json(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    board = {
        "columns": [{"id": "col-1", "title": "Backlog", "cardIds": ["card-1"]}],
        "cards": {"card-1": {"id": "card-1", "title": "Task", "details": "Notes"}},
    }

    upsert_board_for_user("user", board, db_path)
    loaded_board = get_board_for_user("user", db_path)
    assert loaded_board == board

    updated_board = {
        "columns": [{"id": "col-1", "title": "In Progress", "cardIds": []}],
        "cards": {},
    }
    upsert_board_for_user("user", updated_board, db_path)
    reloaded_board = get_board_for_user("user", db_path)
    assert reloaded_board == updated_board


def test_db_file_auto_created_if_missing(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "pm.db"
    assert not db_path.exists()

    upsert_board_for_user("user", {"columns": [], "cards": {}}, db_path)

    assert db_path.exists()
