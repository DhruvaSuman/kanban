# Project Plan Checklist

This file is the execution plan for the MVP. Work proceeds phase-by-phase in order, with user approval required after each phase.

## Phase 1: Plan and Frontend Documentation

### Goals
- Expand this plan into concrete checklists with test and success criteria.
- Add one `frontend/AGENTS.md` describing the existing frontend code.

### Checklist
- [x] Rewrite `docs/PLAN.md` with detailed steps for phases 1-10.
- [x] Include explicit test commands for each phase (backend/frontend/integration as applicable).
- [x] Include phase-level success criteria for each phase.
- [x] Create `frontend/AGENTS.md` with concise architecture and testing notes.

### Tests
- Manual review only in this phase.

### Success Criteria
- `docs/PLAN.md` is detailed enough to execute without guessing.
- `frontend/AGENTS.md` exists and reflects the current frontend implementation.

### Approval Gate
- Stop and request user approval before starting Phase 2.

## Phase 2: Scaffolding (Docker + Backend Hello World)

### Goals
- Create Dockerized runtime and backend skeleton.
- Serve static hello page and expose at least one API route.
- Provide start/stop scripts for macOS, Linux, and Windows.

### Checklist
- [x] Add `backend/` FastAPI app structure.
- [x] Add `Dockerfile` and supporting config to run backend in container.
- [x] Add basic static hello page served by backend.
- [x] Add hello API route (for example `/api/health` or `/api/hello`).
- [x] Add scripts in `scripts/` to start and stop locally on macOS/Linux/Windows.
- [x] Verify container boots cleanly.

### Tests
- [x] Build container image.
- [x] Run container and verify `GET /` serves hello HTML.
- [x] Run container and verify hello API route returns expected JSON.
- [x] Run backend tests (if present at this stage).

### Success Criteria
- Local container starts with one command/script.
- Both static page and API route are reachable and correct.
- Stop scripts cleanly stop running services.

### Approval Gate
- Stop and request user approval before starting Phase 3.

## Phase 3: Integrate Existing Frontend at `/`

### Goals
- Build frontend statically and serve it from backend at `/`.
- Preserve current Kanban demo behavior.

### Checklist
- [x] Integrate frontend build output into backend serving path.
- [x] Ensure backend serves frontend app at `/`.
- [x] Keep routing/assets functional under served setup.
- [x] Add/update integration tests for served frontend.

### Tests
- [x] Frontend unit tests.
- [x] Frontend integration/e2e tests.
- [x] Containerized smoke test that `/` shows Kanban board.

### Success Criteria
- Kanban demo renders at `/` when running through backend container.
- Existing frontend interactions still work.
- Unit and e2e coverage for critical behavior pass.

### Approval Gate
- Stop and request user approval before starting Phase 4.

## Phase 4: Dummy Sign-In Flow

### Goals
- Require login (`user` / `password`) before showing Kanban.
- Support logout and return to login screen.

### Checklist
- [x] Add login UI and simple auth state handling.
- [x] Enforce route guard behavior for `/`.
- [x] Add logout action and session reset behavior.
- [x] Keep implementation simple and explicit for MVP.

### Tests
- [x] Frontend unit tests for login form and state transitions.
- [x] E2E tests for successful login, failed login, logout flow.
- [x] Integration smoke test through backend-served app.

### Success Criteria
- App is not accessible without valid credentials.
- Valid credentials show board; logout returns to login.
- Tests cover happy path and common invalid login case.

### Approval Gate
- Stop and request user approval before starting Phase 5.

## Phase 5: Database Model (JSON Format)

### Goals
- Design and implement database schema storing board payload in JSON format.
- Document database design and get user sign-off.

### Checklist
- [x] Define schema for users and single board per user.
- [x] Store Kanban board state as JSON format in persistence layer.
- [x] Create schema/setup initialization path.
- [x] Document approach in `docs/` with examples and rationale.

### Tests
- [x] Backend unit tests for schema creation and JSON read/write.
- [x] Test DB initialization when DB file does not exist.

### Success Criteria
- Schema supports multiple users with one board each.
- Board data is persisted and retrieved in JSON format.
- Documentation is clear and approved by user.

### Approval Gate
- Stop and request user approval before starting Phase 6.

## Phase 6: Backend Kanban API

### Goals
- Implement backend API to read and mutate Kanban per user.
- Ensure DB auto-creation works.

### Checklist
- [x] Add endpoints for fetching board and applying updates.
- [x] Validate request payloads and response contracts.
- [x] Connect endpoints to JSON persistence layer.
- [x] Ensure DB file/schema initializes automatically.

### Tests
- [x] Backend unit tests for service logic.
- [x] Backend API tests for read/update behavior.
- [x] DB-missing startup test proving auto-create behavior.

### Success Criteria
- API supports full board retrieval and update operations.
- Persistence remains correct across restarts.
- Backend tests pass consistently.

### Approval Gate
- Stop and request user approval before starting Phase 7.

## Phase 7: Frontend + Backend Persistence

### Goals
- Move frontend from local in-memory demo data to backend API.
- Make Kanban state persistent.

### Checklist
- [x] Replace local-only board state bootstrap with API bootstrap.
- [x] Wire card/column operations to backend update endpoints.
- [x] Handle loading, optimistic or non-optimistic update flow simply.
- [x] Keep UI behavior and styling consistent.

### Tests
- [x] Frontend unit tests for API integration points.
- [x] E2E tests for persistence across page refresh.
- [x] End-to-end container test for full stack behavior.

### Success Criteria
- User actions persist and reload correctly from backend.
- No regressions in core Kanban interactions.
- Full stack tests pass.

### Approval Gate
- Stop and request user approval before starting Phase 8.

## Phase 8: AI Connectivity via OpenRouter

### Goals
- Add backend integration with OpenRouter using configured model.
- Validate connectivity with simple `2+2` check.

### Checklist
- [ ] Add backend AI client using `OPENROUTER_API_KEY`.
- [ ] Configure model `openai/gpt-oss-120b`.
- [ ] Add minimal endpoint/service method for connectivity checks.
- [ ] Handle and log common API errors clearly.

### Tests
- [ ] Unit tests for request payload construction (mocked).
- [ ] Integration test for `2+2` call (live or gated live test).
- [ ] Failure-path test when key is missing/invalid.

### Success Criteria
- Backend can successfully call OpenRouter model.
- `2+2` connectivity check returns expected/valid output.
- Error handling path is proven by tests.

### Approval Gate
- Stop and request user approval before starting Phase 9.

## Phase 9: Structured Outputs for Chat + Kanban Updates

### Goals
- Always send board JSON + user question + conversation history to AI.
- Receive structured response containing user text plus optional board update.
- Propose and confirm structured schema before implementation.

### Checklist
- [ ] Propose structured output schema for user approval.
- [ ] Add backend prompt + payload builder with board JSON and history.
- [ ] Parse and validate structured AI response.
- [ ] Apply optional board update payload when present.

### Tests
- [ ] Unit tests for schema validation and parser behavior.
- [ ] Unit tests for no-update and update response variants.
- [ ] Integration tests proving board update application from AI output.

### Success Criteria
- Structured response contract is stable and documented.
- AI response always includes user-facing message.
- Optional Kanban updates are safely validated and applied.

### Approval Gate
- Stop and request user approval before starting Phase 10.

## Phase 10: AI Sidebar UX and Live Board Refresh

### Goals
- Build polished sidebar chat UX.
- Reflect AI-driven board updates in UI automatically.

### Checklist
- [ ] Add sidebar chat UI with message history.
- [ ] Connect sidebar to backend AI endpoint.
- [ ] Show assistant responses and loading/error states.
- [ ] Refresh board state automatically when AI returns updates.
- [ ] Ensure visual style follows project color scheme.

### Tests
- [ ] Frontend unit tests for chat widget interactions.
- [ ] E2E tests for end-to-end chat request and response rendering.
- [ ] E2E/integration test proving AI board update appears in UI.

### Success Criteria
- Chat sidebar is usable and visually consistent.
- AI responses are shown reliably.
- Any AI-triggered board updates appear in the board without manual reload.

### Approval Gate
- Final review and user sign-off on MVP completion.