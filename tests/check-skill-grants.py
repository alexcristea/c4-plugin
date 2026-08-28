#!/usr/bin/env python3
"""Assert that every declared tool grant can actually match at permission-check time.

Claude Code matches Bash permissions on the *expanded command-string prefix*:
`Bash(git:*)` means "bash, git commands only", and `Bash(git status:*)` narrows
further. A grant like `Bash(scripts/validate-dsl.sh:*)` therefore matches nothing,
because the skill body invokes `${CLAUDE_PLUGIN_ROOT}/scripts/validate-dsl.sh`,
which expands to an absolute path under the plugin cache. The grant looks correct,
CI sees a well-formed frontmatter key, and every "pre-approved" run prompts anyway.

The working pattern -- the one the official plugin-dev skill documents -- is to
invoke through the interpreter and grant the interpreter:

    allowed-tools: ..., Bash(bash:*)
    bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-dsl.sh <args>

Both halves are required, so both are checked here. Granting `Bash(bash:*)` while
invoking the script directly still fails to match, and vice versa.

Usage: python3 tests/check-skill-grants.py
Exit 0 if every grant is satisfiable, 1 otherwise.
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/scripts/[A-Za-z0-9_.-]+\.sh")
# A grant naming a bare path rather than a command; can never match.
PATH_GRANT = re.compile(r"Bash\((?![a-z0-9_-]+[:)])[^)]*\)")
# A script path with no ${CLAUDE_PLUGIN_ROOT} prefix. Worse than a bad grant:
# it resolves against the user's project directory, where the script is absent,
# so the step fails outright rather than merely prompting.
BARE_REF = re.compile(r"(?<!\{CLAUDE_PLUGIN_ROOT\}/)(?<![\w./-])scripts/[A-Za-z0-9_.-]+\.sh")


def frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    return m.group(1) if m else ""


def check_skill(path: pathlib.Path) -> list[str]:
    text = path.read_text()
    fm = frontmatter(text)
    body = text[len(fm) + 8:] if fm else text
    rel = path.relative_to(REPO)
    problems: list[str] = []

    grants = ""
    for line in fm.splitlines():
        if line.startswith("allowed-tools:"):
            grants = line.split(":", 1)[1].strip()

    for bad in PATH_GRANT.findall(grants):
        problems.append(
            f"{rel}: grant {bad} names a path, not a command -- it can never match. "
            f"Use Bash(bash:*) and invoke via `bash ${{CLAUDE_PLUGIN_ROOT}}/...`."
        )

    # Every script reference must be invoked through `bash `, so that the command
    # prefix seen by the permission check is "bash". Line numbers come from the
    # whole file, not the body slice, so they match what an editor shows.
    fm_end = len(fm.splitlines()) + 2 if fm else 0
    for lineno, line in enumerate(text.splitlines(), start=1):
        if lineno <= fm_end:
            continue
        for ref in SCRIPT_REF.finditer(line):
            before = line[:ref.start()]
            if not before.rstrip().endswith("bash") or not before.endswith(" "):
                problems.append(
                    f"{rel}:{lineno}: `{ref.group()}` is not invoked via `bash `; "
                    f"the command prefix will be the absolute path, which Bash(bash:*) "
                    f"cannot match."
                )
        for ref in BARE_REF.finditer(line):
            problems.append(
                f"{rel}:{lineno}: `{ref.group()}` lacks ${{CLAUDE_PLUGIN_ROOT}}; it "
                f"resolves against the user's project directory, where the script does "
                f"not exist, so the step fails rather than prompting."
            )

    if SCRIPT_REF.search(body) and "Bash(bash:*)" not in grants:
        problems.append(
            f"{rel}: body invokes a bundled script but allowed-tools lacks Bash(bash:*)."
        )

    return problems


def check_contributing() -> list[str]:
    """The skeleton contributors copy is what propagates this defect."""
    path = REPO / "CONTRIBUTING.md"
    problems = []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        if "allowed-tools:" in line and PATH_GRANT.search(line):
            problems.append(
                f"CONTRIBUTING.md:{lineno}: template grants a path, not a command. "
                f"New skills copied from here inherit a grant that never matches."
            )
    return problems


def main() -> int:
    problems: list[str] = []
    for skill in sorted((REPO / "skills").glob("*/SKILL.md")):
        problems.extend(check_skill(skill))
    problems.extend(check_contributing())

    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        print(f"\n{len(problems)} unsatisfiable grant(s).", file=sys.stderr)
        return 1

    print(f"ok: all skill grants are satisfiable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
