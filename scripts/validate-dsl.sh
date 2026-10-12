#!/usr/bin/env bash
#
# Validate a Structurizr DSL workspace by running structurizr/structurizr (vNext)
# in Docker.
#
# Usage:
#   validate-dsl.sh                       # validates ./workspace.dsl
#   validate-dsl.sh path/to/workspace.dsl
#
# Note: --platform linux/amd64 is required on Apple Silicon (ARM) Macs
# because the image does not have a native ARM build.
#
# --user runs the container as the host user: the image defaults to a non-root
# uid (65532) that cannot write to bind-mounted host dirs on Linux.
#
# STRUCTURIZR_THEMES enables the prebuilt cloud themes bundled in the image, so a
# workspace can say `theme amazon-web-services-2025.07` (the hosted theme URLs on
# static.structurizr.com went away with the cloud service EOL).

set -euo pipefail

WORKSPACE="${1:-workspace.dsl}"

if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker is not installed or not on PATH" >&2
  echo "       install Docker Desktop or the Docker Engine, then re-run." >&2
  exit 127
fi

if ! docker info >/dev/null 2>&1; then
  echo "error: docker daemon is not running" >&2
  exit 1
fi

if [ ! -f "$WORKSPACE" ]; then
  echo "error: $WORKSPACE does not exist" >&2
  exit 2
fi

# structurizr/structurizr mounts the workspace dir at /usr/local/structurizr;
# pass the DSL path relative to that mount.
WORKSPACE_DIR="$(cd "$(dirname "$WORKSPACE")" && pwd)"
WORKSPACE_FILE="$(basename "$WORKSPACE")"

docker run --rm --platform linux/amd64 \
  --user "$(id -u):$(id -g)" \
  -e STRUCTURIZR_THEMES=/usr/local/structurizr-themes \
  -v "${WORKSPACE_DIR}:/usr/local/structurizr" \
  structurizr/structurizr \
  validate -w "/usr/local/structurizr/${WORKSPACE_FILE}"
