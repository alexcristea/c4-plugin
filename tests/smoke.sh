#!/usr/bin/env bash
#
# End-to-end smoke test for the c4-architect plugin's shell tooling and templates.
#
# What it tests
# -------------
# Simulates what /c4:structurize does (copy template + placeholder substitution), then
# exercises validate, export, and preview against the seeded workspace — in both
# standalone and embedded layouts. Catches template corruption, placeholder bugs,
# script regressions, and Docker-side problems without involving Claude itself.
#
# Run from anywhere:
#   tests/smoke.sh
#
# Requirements
# ------------
# - Docker daemon running.
# - Port 8081 (override with C4_SMOKE_PORT=<n>) free.
# - No existing container named "c4-architect-local" (the preview script's fixed
#   name). The script refuses to run if one is present, to avoid clobbering a
#   real preview the user has running.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK_BASE="$(mktemp -d)"
PORT="${C4_SMOKE_PORT:-8081}"
CONTAINER_NAME="c4-architect-local"   # must match scripts/preview-start.sh

cleanup() {
  # On any exit, remove the preview container if WE started one. We detect
  # ours by name; refusing-to-start guard above ensures we never inherit a
  # pre-existing container.
  if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -qx "$CONTAINER_NAME"; then
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
  fi
  rm -rf "$WORK_BASE"
}
trap cleanup EXIT

step() {
  echo
  echo "=== $* ==="
}

fail() {
  echo "smoke: error: $*" >&2
  exit 1
}

# --- preflight ---------------------------------------------------------------

if ! command -v docker >/dev/null 2>&1; then
  fail "docker is required"
fi

if ! docker info >/dev/null 2>&1; then
  fail "docker daemon is not running"
fi

if ! command -v curl >/dev/null 2>&1; then
  fail "curl is required"
fi

if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  fail "a container named '$CONTAINER_NAME' already exists. Run scripts/preview-stop.sh first."
fi

# --- helpers ----------------------------------------------------------------

substitute_placeholders() {
  local dir="$1" name="$2"
  local today
  today="$(date +%Y-%m-%d)"
  # -i.bak is portable across GNU sed (Linux/CI) and BSD sed (macOS).
  find "$dir" -type f \( -name '*.md' -o -name '*.dsl' \) -print0 \
    | xargs -0 sed -i.bak \
        -e "s/{{PROJECT_NAME}}/${name}/g" \
        -e "s/{{TODAY}}/${today}/g"
  find "$dir" -name '*.bak' -delete
}

run_init_flow() {
  local mode="$1" workspace_dir="$2" project_name="$3"

  step "[$mode] copy templates to $workspace_dir"
  mkdir -p "$workspace_dir"
  cp -R "${PLUGIN_ROOT}/templates/workspace/." "$workspace_dir/"
  substitute_placeholders "$workspace_dir" "$project_name"

  # Confirm no placeholders survived.
  # Use grep -E for portable ERE — BRE \+ is literal on BSD/macOS grep.
  if grep -rE '\{\{[A-Z_]+\}\}' "$workspace_dir" >/dev/null 2>&1; then
    grep -rEn '\{\{[A-Z_]+\}\}' "$workspace_dir" >&2 || true
    fail "[$mode] unsubstituted placeholders remain"
  fi

  step "[$mode] validate the seeded workspace"
  "${PLUGIN_ROOT}/scripts/validate-dsl.sh" "${workspace_dir}/workspace.dsl"

  step "[$mode] export PlantUML"
  "${PLUGIN_ROOT}/scripts/export-diagrams.sh" plantuml \
    "${workspace_dir}/workspace.dsl" "${workspace_dir}/build/diagrams"
  if ! ls "${workspace_dir}/build/diagrams/"*.puml >/dev/null 2>&1; then
    fail "[$mode] no .puml files produced under ${workspace_dir}/build/diagrams/"
  fi
}

run_preview_flow() {
  local mode="$1" workspace_dir="$2"

  step "[$mode] start preview on port $PORT"
  C4_PREVIEW_PORT="$PORT" "${PLUGIN_ROOT}/scripts/preview-start.sh" "$workspace_dir"

  echo "smoke: waiting for http://localhost:${PORT} ..."
  local i ok=0
  for i in $(seq 1 60); do
    if curl -sf "http://localhost:${PORT}" >/dev/null 2>&1; then
      echo "smoke: preview up after ${i}s"
      ok=1
      break
    fi
    sleep 1
  done
  if [ "$ok" -ne 1 ]; then
    echo "smoke: docker logs (last 20 lines):" >&2
    docker logs "$CONTAINER_NAME" 2>&1 | tail -20 >&2 || true
    fail "[$mode] preview did not respond on port ${PORT} after 60s"
  fi

  step "[$mode] stop preview"
  "${PLUGIN_ROOT}/scripts/preview-stop.sh"
}

# --- standalone simulation --------------------------------------------------

STANDALONE_DIR="${WORK_BASE}/standalone"
run_init_flow standalone "$STANDALONE_DIR" "SmokeStandalone"
run_preview_flow standalone "$STANDALONE_DIR"

# --- embedded simulation ----------------------------------------------------

EMBEDDED_PARENT="${WORK_BASE}/embedded"
EMBEDDED_DIR="${EMBEDDED_PARENT}/architecture"
mkdir -p "$EMBEDDED_PARENT"
# Simulate an existing project at the parent root so 'embedded' is realistic.
echo "this represents an existing project root" > "${EMBEDDED_PARENT}/Dockerfile"
run_init_flow embedded "$EMBEDDED_DIR" "SmokeEmbedded"
run_preview_flow embedded "$EMBEDDED_DIR"

step "smoke test passed"
