#!/usr/bin/env python3
"""Summarise measure_routing.py output as a routing confusion matrix.

Usage: python3 evals/report_routing.py routing-results.json [--compare before.json]
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib

SKILLS = ["structurize", "update", "validate", "export", "preview", "conventions"]


def load(path: str) -> list[dict]:
    return json.loads(pathlib.Path(path).read_text())


def accuracy(rows: list[dict]) -> dict[str | None, tuple[int, int]]:
    """expected -> (correct, total)."""
    agg: dict[str | None, list[int]] = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        agg[r["expected"]][1] += 1
        agg[r["expected"]][0] += int(bool(r["correct"]))
    return {k: (v[0], v[1]) for k, v in agg.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--compare", help="an earlier results.json to diff against")
    args = ap.parse_args()

    rows = load(args.results)
    errs = [r for r in rows if r.get("error")]

    print(f"{len(rows)} sessions, {sum(r['correct'] for r in rows)} routed correctly "
          f"({sum(r['correct'] for r in rows) / len(rows):.0%})")
    if errs:
        print(f"warning: {len(errs)} session(s) errored or timed out")
    # Single-skill runs: `c4` fired but no workflow file was read before the
    # stream ended. These show as "(none)" below but are a dispatch miss, not
    # a trigger miss.
    undispatched = [r for r in rows if r["skills"] == ["c4"]]
    if undispatched:
        print(f"note: {len(undispatched)} session(s) invoked `c4` but read no workflow")
    print()

    # Confusion matrix: rows = expected, cols = what actually fired.
    cols = SKILLS + ["(none)"]
    width = max(len(c) for c in cols) + 1
    print("routing confusion matrix (row = expected, col = fired)")
    print(" " * 13 + "".join(c[:width - 1].rjust(width) for c in cols))
    for exp in SKILLS + [None]:
        subset = [r for r in rows if r["expected"] == exp]
        if not subset:
            continue
        counts = collections.Counter(r["fired"] or "(none)" for r in subset)
        label = (exp or "(distractor)")[:12].ljust(13)
        cells = "".join(str(counts.get(c, 0) or ".").rjust(width) for c in cols)
        ok, tot = accuracy(rows)[exp]
        print(f"{label}{cells}   {ok}/{tot}")
    print()

    print("per-skill routing accuracy")
    acc = accuracy(rows)
    for exp in SKILLS + [None]:
        if exp not in acc:
            continue
        ok, tot = acc[exp]
        bar = "#" * round(ok / tot * 20)
        print(f"  {(exp or '(distractor)'):<13} {ok:>2}/{tot:<3} {ok/tot:>4.0%} {bar}")
    print()

    misses = [r for r in rows if not r["correct"]]
    if misses:
        print(f"misroutes ({len(misses)})")
        for r in sorted(misses, key=lambda r: str(r["expected"])):
            print(f"  exp={str(r['expected'] or '-'):<12} got={str(r['fired'] or '-'):<12} "
                  f"{r['query'][:70]}")

    if args.compare:
        before = accuracy(load(args.compare))
        print("\nchange vs", args.compare)
        for exp in SKILLS + [None]:
            if exp not in acc or exp not in before:
                continue
            b_ok, b_tot = before[exp]
            a_ok, a_tot = acc[exp]
            delta = a_ok / a_tot - b_ok / b_tot
            arrow = "+" if delta > 0 else ("-" if delta < 0 else " ")
            print(f"  {(exp or '(distractor)'):<13} {b_ok}/{b_tot} -> {a_ok}/{a_tot}  {arrow}{abs(delta):.0%}")


if __name__ == "__main__":
    main()
