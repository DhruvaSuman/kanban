#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="pm-mvp-app"

if docker ps -a --format '{{.Names}}' | awk -v n="${CONTAINER_NAME}" '$0 == n { found=1 } END { exit !found }'; then
  docker rm -f "${CONTAINER_NAME}"
  echo "Stopped ${CONTAINER_NAME}"
else
  echo "No running container named ${CONTAINER_NAME}"
fi
