#!/usr/bin/env python3
"""Assert that template docs and ADRs use the heading levels Structurizr expects.

Supplementary docs (`!docs`) and ADRs (`!adrs`) are imported differently:

- Docs: Structurizr hides every `#` heading and generates the top-level heading
  from the workspace/system/container name. `##` renders as section `1 Name`,
  `###` as `1.1 Name`. So a doc starts at `##`, has no `#` heading, and carries
  no hand-written number (Structurizr numbers sections itself).
  https://docs.structurizr.com/server/documentation/headings
- ADRs: the default adr-tools importer reads the title from `# <number>. <title>`.

Usage: python3 tests/check-doc-headings.py
Exit 0 if every file conforms, 1 otherwise.
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "templates" / "workspace"


def headings(path: pathlib.Path) -> list[str]:
    """Return Markdown ATX headings, skipping fenced code blocks."""
    found, in_fence = [], False
    for line in path.read_text().splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and re.match(r"#{1,6} ", line):
            found.append(line)
    return found


def check_doc(path: pathlib.Path) -> list[str]:
    hs = headings(path)
    if not hs:
        return [f"{path}: no headings"]
    errors = [f"{path}: '{h}' is hidden by Structurizr; start docs at '##'" for h in hs if h.startswith("# ")]
    if not hs[0].startswith("## "):
        errors.append(f"{path}: first heading '{hs[0]}' must be '##'")
    elif re.match(r"## \d", hs[0]):
        errors.append(f"{path}: '{hs[0]}' is numbered by hand; Structurizr numbers sections")
    return errors


def check_adr(path: pathlib.Path) -> list[str]:
    hs = headings(path)
    if not hs or not re.match(r"# \d+\. \S", hs[0]):
        return [f"{path}: first heading must be '# <number>. <title>' (adr-tools format)"]
    return []


def main() -> int:
    failures = []
    for doc in sorted((TEMPLATE / "docs").glob("*.md")):
        errs = check_doc(doc)
        failures += errs
        if not errs:
            print(f"ok: {doc.relative_to(REPO)}")
    for adr in sorted((TEMPLATE / "adrs").glob("*.md")):
        errs = check_adr(adr)
        failures += errs
        if not errs:
            print(f"ok: {adr.relative_to(REPO)}")
    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
