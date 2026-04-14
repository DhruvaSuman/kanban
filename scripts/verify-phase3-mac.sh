#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"

cleanup() {
  bash "${ROOT_DIR}/scripts/stop-mac.sh" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "==> [1/5] Running backend tests"
(
  cd "${BACKEND_DIR}"
  uv run pytest
)

echo "==> [2/5] Installing frontend dependencies"
(
  cd "${FRONTEND_DIR}"
  npm install
)

echo "==> [3/5] Running frontend tests (unit + e2e)"
(
  cd "${FRONTEND_DIR}"
  npx playwright install --with-deps chromium
  npm run test:unit
  npm run test:e2e
)

echo "==> [4/5] Building and starting Docker app"
(
  cd "${ROOT_DIR}"
  bash "scripts/start-mac.sh"
)

echo "==> [5/5] Verifying endpoints"
sleep 2

ROOT_HTML="$(curl -sS http://localhost:8000/)"
if ! awk 'index($0, "Kanban Studio") > 0 { found=1 } END { exit !found }' <<<"${ROOT_HTML}"; then
  echo "ERROR: Root page does not contain 'Kanban Studio'."
  exit 1
fi

HEALTH_JSON="$(curl -sS http://localhost:8000/api/health)"
if [[ "${HEALTH_JSON}" != '{"status":"ok"}' ]]; then
  echo "ERROR: Unexpected /api/health response: ${HEALTH_JSON}"
  exit 1
fi

HELLO_JSON="$(curl -sS http://localhost:8000/api/hello)"
if [[ "${HELLO_JSON}" != '{"message":"hello from fastapi"}' ]]; then
  echo "ERROR: Unexpected /api/hello response: ${HELLO_JSON}"
  exit 1
fi

echo "All Phase 1-3 checks passed."
