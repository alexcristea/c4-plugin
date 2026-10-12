#!/usr/bin/env bash
#
# Maintainer tool: list upstream Structurizr DSL doc changes since the bundled
# references/ were last synced.
#
# The bundled references are curated excerpts, not copies, so a whole-file diff
# is noise. Instead this reads the baseline commit from references/.upstream-sha,
# asks GitHub for every commit touching dsl/ since then, and prints each one's
# dsl/ patches. Patches are also saved to a directory that is kept after exit.
#
# Does NOT modify references/. After applying changes by hand, record the new
# baseline:
#   echo <newest-sha> > references/.upstream-sha
#
# Usage:
#   scripts/update-references.sh
#
# Set GITHUB_TOKEN to avoid the unauthenticated API rate limit.

set -euo pipefail

REPO="structurizr/structurizr.github.io"
API="https://api.github.com/repos/${REPO}"

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SHA_FILE="${PLUGIN_ROOT}/references/.upstream-sha"

for tool in curl python3; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "error: $tool is required" >&2
    exit 127
  fi
done

if [ ! -f "$SHA_FILE" ]; then
  echo "error: $SHA_FILE not found" >&2
  exit 1
fi
BASELINE="$(tr -d '[:space:]' < "$SHA_FILE")"

gh_get() {
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    curl -fsSL -H "Authorization: Bearer ${GITHUB_TOKEN}" "$1"
  else
    curl -fsSL "$1"
  fi
}

OUT_DIR="$(mktemp -d)"
echo "baseline: ${BASELINE}"
echo

# Commits on dsl/, newest first, up to (not including) the baseline.
# Note: plain `commits` is used instead of `compare` so cookbook-only changes
# under dsl/ are included and unrelated repo churn is not.
gh_get "${API}/commits?path=dsl&per_page=100" > "${OUT_DIR}/commits.json"
NEW_SHAS="$(python3 - "$BASELINE" "${OUT_DIR}/commits.json" <<'EOF'
import json, sys
baseline, path = sys.argv[1], sys.argv[2]
commits = json.load(open(path))
found = False
for c in commits:
    if c["sha"].startswith(baseline):
        found = True
        break
    print(c["sha"])
if not found:
    sys.exit("error: baseline not in the latest 100 dsl/ commits; review upstream manually")
EOF
)"

if [ -z "$NEW_SHAS" ]; then
  echo "references/ are up to date with upstream dsl/."
  rm -rf "$OUT_DIR"
  exit 0
fi

for sha in $NEW_SHAS; do
  gh_get "${API}/commits/${sha}" > "${OUT_DIR}/${sha}.json"
  python3 - "${OUT_DIR}/${sha}.json" <<'EOF' | tee "${OUT_DIR}/${sha}.patch"
import json, sys
c = json.load(open(sys.argv[1]))
print(f"## {c['sha'][:7]} {c['commit']['committer']['date'][:10]} {c['commit']['message'].splitlines()[0]}")
for f in c["files"]:
    if f["filename"].startswith("dsl/"):
        print(f"--- {f['filename']}")
        print(f.get("patch", "(no textual patch)"))
print()
EOF
done

echo "newest upstream commit: $(echo "$NEW_SHAS" | head -1)"
echo "patches kept in: ${OUT_DIR}"
echo "Apply relevant changes to references/ by hand, then update references/.upstream-sha."
