#!/usr/bin/env bash
#
# Stop the Structurizr Local container started by preview-start.sh.
# Idempotent: silently succeeds if no container is running.

set -euo pipefail

CONTAINER_NAME="c4-architect-local"

if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker is not installed or not on PATH" >&2
  exit 127
fi

if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  docker rm -f "$CONTAINER_NAME" >/dev/null
  echo "preview stopped"
else
  echo "no preview container running"
fi
