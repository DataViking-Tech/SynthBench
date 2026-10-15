#!/usr/bin/env python3
"""Report how much of the leaderboard the committed Groups data covers.

site/src/data/group-alignment.json is built from raw survey data CI doesn't
have (scripts/build-group-alignment.py), so it's committed and keyed by
config_id. CI regenerates leaderboard.json on every build; when the two drift,
the Groups page silently loses systems (it once showed "1 of 1 systems").

Run after `synthbench publish-data`. Emits a GitHub warning annotation per
dataset below full coverage, and fails only with --min-coverage when a
dataset falls under that share.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("subpop", "opinionsqa", "globalopinionqa")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--leaderboard", type=Path, default=ROOT / "site/src/data/leaderboard.json"
    )
    ap.add_argument(
        "--groups", type=Path, default=ROOT / "site/src/data/group-alignment.json"
    )
    ap.add_argument(
        "--min-coverage",
        type=float,
        default=0.0,
        help="fail if any dataset's covered share is below this (0-1)",
    )
    args = ap.parse_args()

    entries = json.loads(args.leaderboard.read_text(encoding="utf-8"))["entries"]
    systems = json.loads(args.groups.read_text(encoding="utf-8"))["systems"]

    failed = False
    for ds in DATASETS:
        ids = {e["config_id"] for e in entries if e["dataset"] == ds}
        if not ids:
            continue
        covered = len(ids & systems.keys())
        line = f"group-alignment covers {covered}/{len(ids)} {ds} leaderboard configs"
        print(line)
        if covered < len(ids):
            print(
                f"::warning title=Groups data out of date::{line}. "
                "Re-run scripts/build-group-alignment.py with the raw survey data."
            )
        if covered / len(ids) < args.min_coverage:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
