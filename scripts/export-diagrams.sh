#!/usr/bin/env bash
#
# Render diagrams from a Structurizr DSL workspace via structurizr/structurizr
# (vNext) in Docker.
#
# Usage:
#   export-diagrams.sh <format> [workspace.dsl] [output_dir]
#
# Supported formats (per `structurizr/structurizr export -help`):
#   plantuml, plantuml/structurizr, plantuml/c4plantuml,
#   mermaid, websequencediagrams, json, theme, static, fqcn
# Output dir defaults to ./build/diagrams.
#
# Note: --platform linux/amd64 is required on Apple Silicon (ARM) Macs
# because the image does not have a native ARM build.

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: $0 <format> [workspace.dsl] [output_dir]" >&2
  echo "  format examples: plantuml, mermaid, json" >&2
  exit 64
fi

FORMAT="$1"
WORKSPACE="${2:-workspace.dsl}"
OUTPUT_DIR="${3:-build/diagrams}"

if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker is not installed or not on PATH" >&2
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

mkdir -p "$OUTPUT_DIR"

WORKSPACE_DIR="$(cd "$(dirname "$WORKSPACE")" && pwd)"
WORKSPACE_FILE="$(basename "$WORKSPACE")"
OUTPUT_DIR_ABS="$(cd "$OUTPUT_DIR" && pwd)"

docker run --rm --platform linux/amd64 \
  -v "${WORKSPACE_DIR}:/usr/local/structurizr" \
  -v "${OUTPUT_DIR_ABS}:/usr/local/structurizr/out" \
  structurizr/structurizr \
  export \
    -w "/usr/local/structurizr/${WORKSPACE_FILE}" \
    -f "$FORMAT" \
    -o "/usr/local/structurizr/out"

echo "exported $FORMAT diagrams to $OUTPUT_DIR"
