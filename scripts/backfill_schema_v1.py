"""Stamp legacy leaderboard submissions as schema_version=1.

The validator now graduates RAW_RESPONSES_MISSING and RAW_RESPONSES_MODE to
ERROR for v2 submissions (sb-88fw). Existing leaderboard files predate the
graduation: they were generated before the runner reliably persisted raw
model output, so they have no `raw_responses`. Mark them explicitly as
v1 so the legacy WARNING path keeps applying. Files that already declare
a schema_version are left untouched.

Idempotent. Run once after the schema bump lands. Usage:

    python scripts/backfill_schema_v1.py [DIR ...]

DIR defaults to ``leaderboard-results/``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def stamp_v1(path: Path) -> bool:
    """Add ``schema_version: 1`` to a submission JSON if missing.

    Returns True when the file was rewritten.
    """
    try:
        text = path.read_text()
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    if data.get("benchmark") != "synthbench":
        return False
    if "schema_version" in data:
        return False
    new = {"benchmark": data["benchmark"], "schema_version": 1}
    for key, value in data.items():
        if key == "benchmark":
            continue
        new[key] = value
    path.write_text(json.dumps(new, indent=2) + ("\n" if text.endswith("\n") else ""))
    return True


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]] or [Path("leaderboard-results")]
    rewritten = 0
    skipped = 0
    for target in targets:
        if target.is_file():
            files = [target]
        elif target.is_dir():
            files = sorted(target.glob("*.json"))
        else:
            print(f"skip: {target} (not a file or directory)", file=sys.stderr)
            continue
        for f in files:
            if stamp_v1(f):
                rewritten += 1
            else:
                skipped += 1
    print(f"backfill complete: rewritten={rewritten} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
