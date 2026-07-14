#!/usr/bin/env python3
"""Generate (and optionally upload) canonical human-distribution artifacts.

Maintainer tool for issue #308. Builds one artifact per gated dataset from
the dataset adapters (local cache first; the adapter downloads from upstream
if the cache is absent) and writes it to the local canonical directory
(``$SYNTHBENCH_HUMAN_DISTRIBUTIONS_DIR`` or
``~/.synthbench/human-distributions``). With ``--upload`` the artifact is
also uploaded to the gated R2 bucket at ``human-distributions/<dataset>.json``
so CI deploys (which have R2 credentials via Doppler) can rehydrate stripped
``leaderboard-results/*.json`` files at publish time.

The artifact is built from the TRUE upstream data via the adapters, never
from result files — result files only ever carry (rounded) copies.

Usage:
    python scripts/generate-canonical-distributions.py                    # all gated
    python scripts/generate-canonical-distributions.py opinionsqa subpop  # subset
    python scripts/generate-canonical-distributions.py --upload           # + R2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from synthbench.datasets.policy import all_policies  # noqa: E402
from synthbench.human_distributions import (  # noqa: E402
    ARTIFACT_KEY_TEMPLATE,
    build_artifact,
    default_local_dir,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "datasets",
        nargs="*",
        help="Dataset names (default: every registered gated dataset).",
    )
    parser.add_argument(
        "--local-dir",
        type=Path,
        default=None,
        help="Output directory (default: the canonical local dir).",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help=(
            "Also upload each artifact to the gated R2 bucket (requires "
            "R2_ACCOUNT_ID/R2_ACCESS_KEY_ID/R2_SECRET_ACCESS_KEY/R2_BUCKET "
            "and the synthbench[r2] extra)."
        ),
    )
    args = parser.parse_args()

    datasets = args.datasets or [
        p.name for p in all_policies() if p.redistribution_policy == "gated"
    ]
    local_dir = args.local_dir or default_local_dir()
    local_dir.mkdir(parents=True, exist_ok=True)

    uploader = None
    if args.upload:
        from synthbench.r2_upload import R2Uploader

        uploader = R2Uploader.from_env()

    failures = 0
    for dataset in datasets:
        try:
            artifact = build_artifact(dataset)
        except Exception as exc:  # adapter/network specific
            print(f"FAIL {dataset}: {exc}", file=sys.stderr)
            failures += 1
            continue
        out_path = local_dir / f"{dataset}.json"
        out_path.write_text(json.dumps(artifact))
        line = f"{dataset}: {artifact['n_questions']} questions -> {out_path}"
        if uploader is not None:
            key = ARTIFACT_KEY_TEMPLATE.format(dataset=dataset)
            uploader.put_json(key, artifact)
            line += f" + r2://{uploader.bucket}/{key}"
        print(line)

    # In the default "every gated dataset" mode, adapters that require
    # manual upstream setup (eurobarometer, michigan, pewtech, wvs) are
    # expected to fail on most machines — report but don't error. Explicitly
    # requested datasets must succeed.
    return 1 if (failures and args.datasets) else 0


if __name__ == "__main__":
    raise SystemExit(main())
