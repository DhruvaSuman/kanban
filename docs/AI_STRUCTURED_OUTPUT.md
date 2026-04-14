# AI Structured Output Contract (Phase 9)

The backend expects every AI chat response to match this JSON structure:

```json
{
  "assistant_message": "string",
  "board_update": {
    "columns": [
      { "id": "string", "title": "string", "cardIds": ["string"] }
    ],
    "cards": {
      "card-id": { "id": "string", "title": "string", "details": "string" }
    }
  }
}
```

Notes:
- `assistant_message` is always required.
- `board_update` can be `null` when no board changes are needed.
- If `board_update` is present, it must include full `columns` and `cards` payload.

Backend behavior:
- Endpoint: `POST /api/ai/chat/{username}`
- Inputs to model:
  - current board JSON
  - user question
  - conversation history
- On valid `board_update`, backend persists the update and returns `board_updated: true`.
- On `board_update: null`, backend returns current board and `board_updated: false`.
