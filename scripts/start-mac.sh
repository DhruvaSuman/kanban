#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="pm-mvp"
CONTAINER_NAME="pm-mvp-app"
PORT="8000"

docker build -t "${IMAGE_NAME}" .

if docker ps -a --format '{{.Names}}' | awk -v n="${CONTAINER_NAME}" '$0 == n { found=1 } END { exit !found }'; then
  docker rm -f "${CONTAINER_NAME}" >/dev/null
fi

ENV_ARGS=()
if [ -f ".env" ]; then
  ENV_ARGS+=(--env-file .env)
fi

docker run -d --name "${CONTAINER_NAME}" -p "${PORT}:8000" "${ENV_ARGS[@]}" "${IMAGE_NAME}"
echo "Running at http://localhost:${PORT}"
