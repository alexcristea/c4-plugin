#!/usr/bin/env python3
"""Measure which c4 skill actually fires for each query in the trigger pool.

Why not skill-creator's run_eval.py: that harness injects a *synthetic* command
carrying one skill's description and asks whether it fires. Two problems here.
It tests each skill alone, so it cannot see one sibling poaching another's
queries -- which is the failure mode this plugin is most at risk of. And with
the real c4 plugin installed, the probe competes with the genuine skill, so the
measurement is contaminated (observed: a single query invoking both `c4:export`
and the probe).

Instead, run the real plugin via `claude -p --plugin-dir <repo>` -- which
overrides the installed copy with the working tree -- and record which c4 skill
Claude reaches for. One run per query exercises all six skills at once, so the
result is a routing confusion matrix rather than six isolated yes/no answers.

With --single-skill DIR it measures the built single-skill package instead
(scripts/build-skill.py): the package is installed as a project skill in a copy
of the workdir, every installed c4 plugin is disabled for the session, and the
"fired" workflow is the first workflows/<name>.md Claude reads (Read or cat) after invoking
the `c4` skill. Same query pool, same output shape, so report_routing.py can
--compare the two.

Usage:
  python3 evals/measure_routing.py [--runs 1] [--workers 5] [--out results.json]
  python3 evals/measure_routing.py --single-skill dist/skill/c4 --out single.json
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ["structurize", "update", "validate", "export", "preview", "conventions"]
MODEL = os.environ.get("C4_EVAL_MODEL", "claude-opus-5[1m]")
TIMEOUT = int(os.environ.get("C4_EVAL_TIMEOUT", "240"))

# Which plugin tree to measure. Defaults to this repo, but can point at an older
# checkout to get a before/after -- the query pool always comes from REPO so both
# runs are scored against the same questions.
PLUGIN_DIR = REPO
# Set by --single-skill: measure the built package instead of the plugin.
SINGLE_SKILL = False
# Absolute or relative: Claude often `cd`s into the skill dir and cats workflows/x.md.
WORKFLOW_READ = re.compile(r"(?<![\w-])workflows/([a-z]+)\.md\b")


def load_pool() -> list[tuple[str, str | None]]:
    """Return (query, expected_skill) pairs. expected_skill is None for distractors."""
    sys.path.insert(0, str(REPO / "evals"))
    from build_trigger_evals import POSITIVES, DISTRACTORS  # noqa: E402

    pool: list[tuple[str, str | None]] = []
    for skill in SKILLS:
        pool.extend((q, skill) for q in POSITIVES[skill])
    pool.extend((q, None) for q in DISTRACTORS)
    return pool


def run_query(query: str, workdir: pathlib.Path) -> dict:
    """Run one query against the working-tree plugin; report the skills invoked.

    Reads the stream incrementally and stops at the first c4 skill invocation.
    Waiting for the session to finish would time out on skills that keep working
    after they trigger -- `structurize` scaffolds files and shells out to Docker,
    which took >240s and registered as "never triggered" when it had in fact
    triggered within the first few seconds. Routing is decided the moment the
    skill is chosen, so there is nothing to gain by watching the rest.
    """
    cmd = [
        "claude", "-p", query,
        "--output-format", "stream-json", "--verbose",
        "--model", MODEL,
    ] + (single_skill_args() if SINGLE_SKILL else ["--plugin-dir", str(PLUGIN_DIR)])
    scan = scan_single if SINGLE_SKILL else scan_plugin
    # CLAUDECODE would make the nested CLI refuse to start; safe for a subprocess.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    started = time.time()
    proc = subprocess.Popen(
        cmd, cwd=workdir, env=env, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )

    skills: list[str] = []
    error = None
    try:
        for raw_line in proc.stdout:
            if time.time() - started > TIMEOUT:
                error = "timeout"
                break
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "assistant":
                if scan(tool_uses(event), skills):
                    break  # routing decided
            elif event.get("type") == "result":
                if event.get("is_error"):
                    error = str(event.get("result"))[:200]
                break
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        proc.stdout.close()

    return {"query": query, "skills": skills, "error": error,
            "seconds": round(time.time() - started, 1)}


def tool_uses(event: dict) -> list[dict]:
    content = event.get("message", {}).get("content", [])
    return [item for item in content if item.get("type") == "tool_use"]


def scan_plugin(uses: list[dict], skills: list[str]) -> bool:
    """Record c4:* skill invocations; routing is decided once one fires."""
    for item in uses:
        name = item.get("input", {}).get("skill", "") if item.get("name") == "Skill" else ""
        # Other plugins' skills may legitimately fire; ignore them.
        if name.startswith("c4:") and name not in skills:
            skills.append(name)
    return bool(skills)


def workflow_read(item: dict) -> str | None:
    """The workflow name if this tool use loads workflows/<name>.md.

    Claude reads it with Read or with `cat` through Bash, about equally often.
    """
    inp = item.get("input", {})
    target = {"Read": inp.get("file_path", ""), "Bash": inp.get("command", "")}.get(item.get("name"), "")
    match = WORKFLOW_READ.search(target)
    return match.group(1) if match else None


def scan_single(uses: list[dict], skills: list[str]) -> bool:
    """Record `c4`, then the first workflow it reads as `c4:<workflow>`.

    Routing inside a single skill happens when Claude picks a workflow file, so
    the decision is the first workflows/<name>.md Read after the skill fires.
    """
    for item in uses:
        if not skills:
            skills.extend(["c4"] if item.get("input", {}).get("skill") == "c4" else [])
        elif workflow := workflow_read(item):
            skills.append(f"c4:{workflow}")
            return True
    return False


def single_skill_args() -> list[str]:
    """Disable every installed c4 plugin so only the project skill can answer."""
    settings = pathlib.Path.home() / ".claude" / "settings.json"
    enabled = json.loads(settings.read_text()).get("enabledPlugins", {}) if settings.exists() else {}
    off = {name: False for name in enabled if name.split("@", 1)[0] == "c4"}
    return ["--settings", json.dumps({"enabledPlugins": off})]


def stage_single_skill(skill_dir: pathlib.Path, workdir: pathlib.Path | None) -> pathlib.Path:
    """Copy workdir (or start empty, for None) to a temp dir with the package as .claude/skills/c4/."""
    staged = pathlib.Path(tempfile.mkdtemp(prefix="c4-single-skill-")) / "ws"
    if workdir:
        shutil.copytree(workdir, staged, ignore=shutil.ignore_patterns(".git"))
    shutil.copytree(skill_dir, staged / ".claude" / "skills" / "c4", dirs_exist_ok=True)
    return staged


def fired_workflow(skills: list[str]) -> str | None:
    """The routed-to workflow: the first c4:<name> entry, or None."""
    named = [s for s in skills if ":" in s]
    return named[0].split(":", 1)[1] if named else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1, help="runs per query")
    ap.add_argument("--workers", type=int, default=5,
                    help="concurrent claude sessions (keep modest; the API rate-limits)")
    ap.add_argument("--out", default="routing-results.json")
    ap.add_argument("--workdir", default=".",
                    help="directory to run queries in; should contain a C4 workspace")
    ap.add_argument("--plugin-dir", default=str(REPO),
                    help="plugin tree to measure (default: this repo). Point at an "
                         "older checkout to get a before/after comparison.")
    ap.add_argument("--single-skill", metavar="DIR",
                    help="measure a built single-skill package (scripts/build-skill.py) "
                         "instead of the plugin")
    args = ap.parse_args()

    global PLUGIN_DIR, SINGLE_SKILL
    PLUGIN_DIR = pathlib.Path(args.plugin_dir).resolve()
    SINGLE_SKILL = bool(args.single_skill)

    workdir = pathlib.Path(args.workdir).resolve()
    skill_dir = pathlib.Path(args.single_skill).resolve() if SINGLE_SKILL else None
    if SINGLE_SKILL:
        workdir = stage_single_skill(skill_dir, workdir)

    def workdir_for(expected: str | None) -> pathlib.Path:
        # The single skill checks the filesystem before picking a workflow, and
        # its dispatch rule sends "set up C4" to update when workspace.dsl exists
        # (scaffolding would overwrite it). Score structurize queries where they
        # make sense: a fresh, empty dir each, so parallel sessions can't see
        # each other's scaffolding. The plugin picks its skill from the
        # description before looking, so it keeps the shared workdir.
        return stage_single_skill(skill_dir, None) if SINGLE_SKILL and expected == "structurize" else workdir
    pool = load_pool()
    jobs = [(q, exp, r) for q, exp in pool for r in range(args.runs)]
    print(f"{len(pool)} queries x {args.runs} run(s) = {len(jobs)} sessions, "
          f"{args.workers} at a time, cwd={workdir}", flush=True)
    print(f"measuring {'single skill: ' + args.single_skill if SINGLE_SKILL else f'plugin: {PLUGIN_DIR}'}",
          flush=True)

    results = []
    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool_exec:
        futures = {pool_exec.submit(run_query, q, workdir_for(exp)): (q, exp)
                   for q, exp, _ in jobs}
        for fut in cf.as_completed(futures):
            q, expected = futures[fut]
            rec = fut.result()
            rec["expected"] = expected
            rec["fired"] = fired_workflow(rec["skills"])
            rec["correct"] = rec["fired"] == expected
            results.append(rec)
            done += 1
            mark = "ok " if rec["correct"] else "MISS"
            print(f"[{done}/{len(jobs)}] {mark} exp={expected or '-':<12} "
                  f"got={rec['fired'] or '-':<12} {rec['seconds']:>5}s  {q[:52]}",
                  flush=True)

    pathlib.Path(args.out).write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
