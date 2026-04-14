#!/usr/bin/env python3
"""Fail-fast post-publish integrity check.

Run after `synthbench publish-data` and `synthbench publish-runs`, before the
Astro build. Guards against stale / path-polluted publish artifacts (sb-4zy)
by asserting every entry carries a `config_id` and every referenced config
has a matching rollup file on disk.

Exits non-zero on first violation. Paths are CLI flags so this can be reused
from CI and local dev.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_json(path: Path) -> object:
    try:
        with path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"FAIL: {path} not found — publish step did not produce it")
    except json.JSONDecodeError as e:
        sys.exit(f"FAIL: {path} is not valid JSON: {e}")


def check_leaderboard(path: Path) -> set[str]:
    data = _load_json(path)
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        sys.exit(f"FAIL: {path} has no 'entries' list or it is empty")

    missing = [i for i, e in enumerate(entries) if not e.get("config_id")]
    if missing:
        sample = entries[missing[0]]
        sys.exit(
            f"FAIL: {len(missing)}/{len(entries)} leaderboard entries missing "
            f"config_id. First offender (idx {missing[0]}): "
            f"provider={sample.get('provider')!r} dataset={sample.get('dataset')!r}"
        )
    return {e["config_id"] for e in entries}


def check_runs_index(path: Path) -> set[str]:
    data = _load_json(path)
    if not isinstance(data, dict):
        sys.exit(f"FAIL: {path} is not a dict")

    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        sys.exit(f"FAIL: {path} has no 'runs' list or it is empty")

    missing = [i for i, r in enumerate(runs) if not r.get("config_id")]
    if missing:
        sample = runs[missing[0]]
        sys.exit(
            f"FAIL: {len(missing)}/{len(runs)} runs-index entries missing "
            f"config_id. First offender: run_id={sample.get('run_id')!r}"
        )

    declared = data.get("n_configs")
    config_ids = {r["config_id"] for r in runs}
    if isinstance(declared, int) and declared != len(config_ids):
        sys.exit(
            f"FAIL: {path} n_configs={declared} but runs reference "
            f"{len(config_ids)} distinct config_ids"
        )
    return config_ids


def check_config_files(config_dir: Path, referenced: set[str]) -> None:
    if not config_dir.is_dir():
        sys.exit(f"FAIL: config rollup directory {config_dir} does not exist")

    on_disk = {p.stem for p in config_dir.glob("*.json")}
    missing_files = referenced - on_disk
    if missing_files:
        sample = sorted(missing_files)[:3]
        sys.exit(
            f"FAIL: {len(missing_files)} config_ids referenced by runs-index "
            f"have no rollup file in {config_dir}. Examples: {sample}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--leaderboard",
        type=Path,
        default=Path("site/src/data/leaderboard.json"),
    )
    parser.add_argument(
        "--runs-index",
        type=Path,
        default=Path("site/public/data/runs-index.json"),
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path("site/public/data/config"),
    )
    args = parser.parse_args()

    leaderboard_ids = check_leaderboard(args.leaderboard)
    runs_ids = check_runs_index(args.runs_index)
    check_config_files(args.config_dir, runs_ids)

    # Every config_id appearing on the leaderboard must also have a rollup
    # file — this is what the /run/[id] and /config/[id] routes hydrate from.
    orphan_on_leaderboard = leaderboard_ids - runs_ids
    if orphan_on_leaderboard:
        sample = sorted(orphan_on_leaderboard)[:3]
        sys.exit(
            f"FAIL: {len(orphan_on_leaderboard)} leaderboard config_ids are "
            f"not represented in runs-index. Examples: {sample}"
        )

    print(
        f"OK: leaderboard={len(leaderboard_ids)} configs, "
        f"runs-index={len(runs_ids)} configs, all config_ids present."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
