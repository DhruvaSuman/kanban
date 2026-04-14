# Database Approach (Phase 5)

This MVP uses SQLite and stores each user's Kanban board payload in JSON format.

## Design Goals
- Keep schema small and easy to evolve.
- Support multiple users.
- Enforce one board per user for MVP.
- Persist full board shape as JSON payload.

## Schema

### `users`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `username` TEXT NOT NULL UNIQUE

### `boards`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id` INTEGER NOT NULL UNIQUE
- `board_json` TEXT NOT NULL
- `updated_at` TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
- Foreign key: `user_id -> users.id`

## Why this works for MVP
- A single JSON field keeps write/read logic simple while backend/frontend contracts settle.
- `user_id` uniqueness guarantees one board per user.
- Schema still supports multiple users naturally.

## JSON payload shape

Stored as serialized JSON string in `boards.board_json`:

```json
{
  "columns": [
    { "id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"] }
  ],
  "cards": {
    "card-1": { "id": "card-1", "title": "Task title", "details": "Task notes" }
  }
}
```

## Initialization behavior
- DB file and parent directories are auto-created when missing.
- Tables are created with `CREATE TABLE IF NOT EXISTS`.

## Current backend helpers
- `init_db(...)`: create DB schema if needed.
- `upsert_board_for_user(...)`: create user if needed and insert/update JSON board.
- `get_board_for_user(...)`: fetch and deserialize JSON board for a username.
