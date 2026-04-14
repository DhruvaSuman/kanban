# Project Management MVP

This repository contains a local MVP project management app with:
- Next.js frontend (Kanban board + AI chat sidebar)
- FastAPI backend (auth-gated board APIs + AI endpoints)
- SQLite persistence
- Docker-based local run flow

## Tech Stack

- Frontend: Next.js, React, TypeScript
- Backend: FastAPI, Python
- Database: SQLite (JSON board payload per user)
- AI: OpenRouter (`openai/gpt-oss-120b`)
- Packaging/runtime: Docker

## Clone and Run

### 1) Clone repository

```bash
git clone https://github.com/DhruvaSuman/kanban.git
cd kanban
```

### 2) Create `.env`

Create `.env` in repo root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 3) Start app

Docker Desktop must be installed and running.

#### macOS
```bash
bash scripts/start-mac.sh
```

#### Linux
```bash
bash scripts/start-linux.sh
```

#### Windows (Command Prompt)
```bat
scripts\start-windows.bat
```

### 4) Open app

- App: `http://localhost:8000`
- Health: `http://localhost:8000/api/health`

### 5) Login credentials

Current MVP authentication is hardcoded.

- Username: `user`
- Password: `password`

## Features Included

- Login gate (MVP hardcoded credentials)
- Kanban board with:
  - fixed columns (renamable)
  - add/delete cards
  - drag-and-drop card movement
- Persistent board storage through backend APIs
- AI chat sidebar:
  - sends board + history + user question to backend AI endpoint
  - receives assistant response
  - applies optional board updates automatically

## Stop App

#### macOS
```bash
bash scripts/stop-mac.sh
```

#### Linux
```bash
bash scripts/stop-linux.sh
```

#### Windows
```bat
scripts\stop-windows.bat
```

## Test Commands

### Backend tests

```bash
cd backend
uv sync
uv run pytest
```

### Frontend tests

```bash
cd frontend
npm install
npx playwright install --with-deps chromium
npm run test:unit
npm run test:e2e
```

### Coverage (optional)

```bash
# backend
cd backend
uv run pytest --cov=. --cov-report=term-missing

# frontend
cd ../frontend
npm run test:unit -- --coverage
```

## Useful APIs

- `GET /api/health`
- `GET /api/board/{username}`
- `PUT /api/board/{username}`
- `GET /api/ai/connectivity`
- `POST /api/ai/chat/{username}`

## Troubleshooting

- If AI chat returns API key errors:
  - confirm `.env` exists at repo root
  - confirm `OPENROUTER_API_KEY` is valid
  - restart using `scripts/start-*.sh` or `scripts/start-windows.bat`
- If Docker fails to start:
  - ensure Docker Desktop is running
  - retry after `scripts/stop-*.sh` / `scripts/stop-windows.bat`
