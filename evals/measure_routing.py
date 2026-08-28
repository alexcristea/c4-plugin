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

Usage:
  python3 evals/measure_routing.py [--runs 1] [--workers 5] [--out results.json]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import subprocess
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
        "--plugin-dir", str(PLUGIN_DIR),
    ]
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
                for item in event.get("message", {}).get("content", []):
                    if item.get("type") == "tool_use" and item.get("name") == "Skill":
                        name = item.get("input", {}).get("skill", "")
                        # Other plugins' skills may legitimately fire; ignore them.
                        if name.startswith("c4:") and name not in skills:
                            skills.append(name)
                if skills:
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
    args = ap.parse_args()

    global PLUGIN_DIR
    PLUGIN_DIR = pathlib.Path(args.plugin_dir).resolve()

    workdir = pathlib.Path(args.workdir).resolve()
    pool = load_pool()
    jobs = [(q, exp, r) for q, exp in pool for r in range(args.runs)]
    print(f"{len(pool)} queries x {args.runs} run(s) = {len(jobs)} sessions, "
          f"{args.workers} at a time, cwd={workdir}", flush=True)
    print(f"measuring plugin: {PLUGIN_DIR}", flush=True)

    results = []
    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool_exec:
        futures = {pool_exec.submit(run_query, q, workdir): (q, exp)
                   for q, exp, _ in jobs}
        for fut in cf.as_completed(futures):
            q, expected = futures[fut]
            rec = fut.result()
            rec["expected"] = expected
            rec["fired"] = rec["skills"][0].split(":", 1)[1] if rec["skills"] else None
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
