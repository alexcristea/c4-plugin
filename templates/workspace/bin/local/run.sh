#!/usr/bin/env bash
#
# Run Structurizr Local (vNext) using Docker.
# See: https://docs.structurizr.com/local
#
# Note: --platform linux/amd64 is required on Apple Silicon (ARM) Macs
# because the image does not have a native ARM build.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker is not installed or not on PATH" >&2
  exit 127
fi

if ! docker info >/dev/null 2>&1; then
  echo "error: docker daemon is not running" >&2
  exit 1
fi

docker run -it --rm --platform linux/amd64 \
  -p 8080:8080 \
  -v "${WORKSPACE_DIR}":/usr/local/structurizr \
  structurizr/structurizr local

# After the container starts, it will serve the web UI at http://localhost:8080/
