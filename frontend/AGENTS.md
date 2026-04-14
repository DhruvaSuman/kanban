# Frontend Agent Notes

## Scope
- This `frontend/` app is a standalone Next.js Kanban demo.
- It currently runs without backend integration and keeps board state in client memory.

## Stack
- Next.js (App Router) with React and TypeScript.
- Tailwind CSS for styling.
- `@dnd-kit` for drag and drop behavior.
- Vitest + Testing Library for unit/component tests.
- Playwright for end-to-end tests.

## Current App Structure
- `src/app/page.tsx` renders `KanbanBoard` as the main page.
- `src/components/KanbanBoard.tsx` owns board UI state and interaction handlers.
- `src/components/KanbanColumn.tsx` and card components render columns/cards and form controls.
- `src/lib/kanban.ts` defines board types, initial data, card move helpers, and ID creation.

## Current Behavior
- Displays a 5-column Kanban board with seeded cards.
- Supports column rename.
- Supports add/delete card actions.
- Supports drag-and-drop card movement within and across columns.
- No sign-in flow yet.
- No backend persistence yet.
- No AI sidebar yet.

## Frontend Test Commands
- Install deps: `npm install`
- Run dev server: `npm run dev`
- Run lint: `npm run lint`
- Run unit tests: `npm run test:unit`
- Run e2e tests: `npm run test:e2e`
- Run full test suite: `npm run test:all`

## Notes for Future Phases
- Keep the existing visual style and interactions stable while integrating backend features.
- Prefer simple, explicit state flow during login and API integration phases.
- Add/adjust tests alongside each behavior change.
