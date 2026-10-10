#!/usr/bin/env python3
"""Score withheld private-holdout rows in a submission (pipeline step).

Runs in process-submission before validation, with R2 credentials so the
canonical answer key is available. Rewrites the file in place. A file with
no withheld rows is left unchanged.

Usage: python scripts/score-withheld-rows.py <result.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from synthbench.human_distributions import load_canonical_distributions
from synthbench.withheld import has_withheld_rows, score_withheld_rows


def main(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not has_withheld_rows(data):
        print("no withheld rows")
        return 0
    dataset = (data.get("config") or {}).get("dataset", "")
    canonical = load_canonical_distributions(dataset)
    if not canonical:
        print(f"error: no canonical answers available for {dataset!r}", file=sys.stderr)
        return 1
    n = score_withheld_rows(data, canonical)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"scored {n} withheld row(s) server-side")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(Path(sys.argv[1])))
