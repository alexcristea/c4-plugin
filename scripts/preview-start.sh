#!/usr/bin/env bash
#
# Start Structurizr Local (vNext) to preview the workspace at http://localhost:8080.
# See: https://docs.structurizr.com/local
#
# Usage:
#   preview-start.sh                 # serves the current directory
#   preview-start.sh path/to/dir     # serves the given directory
#
# The directory must contain a workspace.dsl. Idempotent: re-running while the
# container is up restarts it cleanly. Runs in the background so /c4:preview
# returns control to the user.
#
# Note: --platform linux/amd64 is required on Apple Silicon (ARM) Macs
# because the image does not have a native ARM build.

set -euo pipefail

WORKSPACE_DIR="${1:-.}"
CONTAINER_NAME="c4-architect-local"
PORT="${C4_PREVIEW_PORT:-8080}"

if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker is not installed or not on PATH" >&2
  exit 127
fi

if ! docker info >/dev/null 2>&1; then
  echo "error: docker daemon is not running" >&2
  exit 1
fi

if [ ! -f "${WORKSPACE_DIR}/workspace.dsl" ]; then
  echo "error: no workspace.dsl in ${WORKSPACE_DIR}" >&2
  exit 2
fi

WORKSPACE_DIR_ABS="$(cd "$WORKSPACE_DIR" && pwd)"

# Remove any pre-existing container with the same name.
if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

docker run -d \
  --name "$CONTAINER_NAME" \
  --platform linux/amd64 \
  -p "${PORT}:8080" \
  -v "${WORKSPACE_DIR_ABS}":/usr/local/structurizr \
  structurizr/structurizr local >/dev/null

echo "Preview running at http://localhost:${PORT}"
echo "stop it with: scripts/preview-stop.sh"
