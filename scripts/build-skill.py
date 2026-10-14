#!/usr/bin/env python3
"""Build the plugin into one self-contained skill package.

Single-skill hosts take one SKILL.md plus bundled files, not a plugin with six
skills. This turns the plugin into that shape without forking it:

  templates/skill/SKILL.md  -> SKILL.md (router; gets the "Choosing between" sections)
  skills/<name>/SKILL.md    -> workflows/<name>.md (frontmatter stripped, paths rewritten)
  references/, scripts/, templates/ -> copied verbatim (minus the router source)

The output names no publishing platform; upload the directory wherever a
single skill is accepted. Fails rather than shipping a package with dangling
${CLAUDE_PLUGIN_ROOT} paths or /c4: slash commands.

Usage: python3 scripts/build-skill.py [--out dist/skill/c4]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
from dataclasses import dataclass

REPO = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ["structurize", "update", "validate", "export", "preview", "conventions"]
ASSET_DIRS = ["references", "scripts", "templates"]
ROUTER = "templates/skill/SKILL.md"
# Maintainer-only tooling; meaningless to someone who installed the skill. The
# router source is rendered into SKILL.md, so a verbatim copy would be a stray duplicate.
EXCLUDED = {"scripts/update-references.sh", "scripts/build-skill.py", "references/.upstream-sha", ROUTER}
MARKER = "<!-- choosing-between -->"

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
CHOOSING = re.compile(r"^## Choosing between .*?(?=^## |\Z)", re.DOTALL | re.MULTILINE)

# Plugin-specific sentences that a mechanical rewrite can't fix. Each `old`
# must still exist in the source: a missing one means the source drifted and
# the patch needs revisiting, so the build fails instead of skipping it.
PATCHES = {
    "conventions": [(
        "The `paths:` frontmatter limits this skill to Structurizr DSL files, ADRs, and "
        "supplementary docs, so it stays out of the way on unrelated work.",
        "The `c4` skill loads this file before any edit to a Structurizr DSL file, ADR, or "
        "supplementary doc.",
    )],
    "validate": [("outside this plugin", "outside this skill")],
    "structurize": [
        ("the plugin's templates", "the skill's templates"),
        # Slash commands the user would type; a skill user asks in prose instead.
        ("print a short next-step hint: `/c4:update`, `/c4:validate`, `/c4:preview`.",
         "print a short next-step hint: describe a change to the model, ask to validate, "
         "or ask to preview the diagrams."),
        ("Run /c4:validate when Docker is available.",
         "Ask to validate the workspace when Docker is available."),
    ],
}


class BuildError(Exception):
    pass


@dataclass
class Stats:
    files: int
    bytes: int


def apply_patches(name: str, text: str) -> str:
    for old, new in PATCHES.get(name, []):
        if old not in text:
            raise BuildError(f"{name}: patch target not found: {old[:60]!r}")
        text = text.replace(old, new)
    return text


def read_skill(repo: pathlib.Path, name: str) -> str:
    """A source skill with plugin-only paths, commands, and sentences rewritten."""
    text = apply_patches(name, (repo / "skills" / name / "SKILL.md").read_text())
    text = text.replace("${CLAUDE_PLUGIN_ROOT}", "${CLAUDE_SKILL_DIR}")
    return re.sub(r"/c4:(?=\w)", "c4 ", text)


def to_workflow(source: str) -> str:
    body = FRONTMATTER.sub("", source, count=1).lstrip()
    return CHOOSING.sub("", body)


def render_router(repo: pathlib.Path, sources: dict[str, str]) -> str:
    router = (repo / ROUTER).read_text()
    if MARKER not in router:
        raise BuildError(f"{ROUTER}: missing {MARKER} placeholder")
    sections = [s.strip() for name in SKILLS for s in CHOOSING.findall(sources[name])]
    router = router.replace(MARKER, "\n\n".join(sections))
    version = json.loads((repo / ".claude-plugin" / "plugin.json").read_text())["version"]
    # `metadata` is the one free-form key every skill host accepts.
    return router.replace("\n---\n", f'\nmetadata:\n  version: "{version}"\n---\n', 1)


# Local clutter, never part of the package. __pycache__ appears under scripts/
# as soon as anything imports build-skill.py (the tests do).
JUNK = {"__pycache__", ".DS_Store"}


def shipped(path: pathlib.Path, rel: pathlib.PurePath) -> bool:
    return path.is_file() and rel.as_posix() not in EXCLUDED and not JUNK & set(rel.parts)


def copy_assets(repo: pathlib.Path, out: pathlib.Path) -> None:
    for src in sorted(p for top in ASSET_DIRS for p in (repo / top).rglob("*")):
        rel = src.relative_to(repo)
        if shipped(src, rel):
            (out / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out / rel)


def check_package(out: pathlib.Path) -> Stats:
    files = sorted(p for p in out.rglob("*") if p.is_file())
    for path in files:
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise BuildError(f"{path.relative_to(out)}: not a text file") from None
        if path.suffix == ".md" and "CLAUDE_PLUGIN_ROOT" in text:
            raise BuildError(f"{path.relative_to(out)}: CLAUDE_PLUGIN_ROOT left after rewrite")
    return Stats(files=len(files), bytes=sum(p.stat().st_size for p in files))


def build(repo: pathlib.Path, out: pathlib.Path) -> Stats:
    if out.exists():
        shutil.rmtree(out)
    sources = {name: read_skill(repo, name) for name in SKILLS}
    (out / "workflows").mkdir(parents=True)
    (out / "SKILL.md").write_text(render_router(repo, sources))
    for name, source in sources.items():
        (out / "workflows" / f"{name}.md").write_text(to_workflow(source))
    copy_assets(repo, out)
    return check_package(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(REPO / "dist" / "skill" / "c4"))
    out = pathlib.Path(ap.parse_args().out).resolve()
    try:
        stats = build(REPO, out)
    except BuildError as err:
        print(f"build failed: {err}", file=sys.stderr)
        return 1
    print(f"built {out}: {stats.files} files, {stats.bytes / 1024:.1f} KiB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
