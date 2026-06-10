#!/usr/bin/env bash
#
# Maintainer tool: re-fetch upstream Structurizr DSL docs and print a diff
# against the bundled references/ directory.
#
# Does NOT modify references/ in place — it writes to a tmpdir and runs `diff`
# so the maintainer can review and apply changes deliberately.
#
# Usage:
#   scripts/update-references.sh

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/structurizr/structurizr.github.io/main/dsl"

# Map upstream source -> local reference filename.
# Most bundled references are curated excerpts from 71-language.md.
# Download every upstream source so the maintainer can see the full diff;
# files with no local counterpart print "NEW" and show the raw upstream content.
SOURCES=(
  "03-basics.md:basics.md"
  "04-defaults.md:defaults.md"
  "05-identifiers.md:identifiers.md"
  "06-archetypes.md:archetypes.md"
  "07-implied-relationships.md:implied-relationships.md"
  "08-expressions.md:expressions.md"
  "31-includes.md:includes.md"
  "51-docs.md:docs.md"
  "52-adrs.md:adrs.md"
  "71-language.md:language-full.md"
)

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REFERENCES_DIR="${PLUGIN_ROOT}/references"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

if ! command -v curl >/dev/null 2>&1; then
  echo "error: curl is required" >&2
  exit 127
fi

echo "fetching upstream docs into $TMP_DIR"
for entry in "${SOURCES[@]}"; do
  upstream="${entry%%:*}"
  local_name="${entry##*:}"
  url="${REPO_RAW}/${upstream}"
  echo "  $url -> $local_name"
  curl -fsSL "$url" -o "${TMP_DIR}/${local_name}"
done

echo
echo "diff (upstream vs bundled):"
echo

for entry in "${SOURCES[@]}"; do
  local_name="${entry##*:}"
  upstream_file="${TMP_DIR}/${local_name}"
  bundled_file="${REFERENCES_DIR}/${local_name}"

  if [ ! -f "$bundled_file" ]; then
    echo "## $local_name — NEW (no bundled copy)"
    continue
  fi

  if diff -u "$bundled_file" "$upstream_file" >/dev/null 2>&1; then
    echo "## $local_name — up to date"
  else
    echo "## $local_name — differs"
    diff -u "$bundled_file" "$upstream_file" || true
    echo
  fi
done

echo
echo "Upstream copies left in: $TMP_DIR (cleaned on exit)"
echo "Review the diff and update references/ by hand."
