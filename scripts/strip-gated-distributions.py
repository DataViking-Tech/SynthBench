#!/usr/bin/env python3
"""Strip gated per-question ``human_distribution`` from committed result files.

License-restricted (``gated``) datasets — OpinionsQA / SubPOP /
GlobalOpinionQA (Pew ATP, CC-BY-NC-SA sources) — must not have their
per-question ``human_distribution`` redistributed via the public git repo
(issue #308). This script removes the field from result JSONs in place and
stamps a top-level ``"stripped_fields": ["human_distribution"]`` marker so
the validator knows the omission is deliberate.

Everything else is preserved: ``model_distribution``, per-question metrics
(``jsd`` / ``kendall_tau`` / ``parity``), ``human_refusal_rate`` (a derived
scalar, like the metrics — required to recompute ``p_refuse``), keys, text,
options. Full-tier datasets (gss, ntia) are policy-driven and left intact.

Idempotent: re-running on already-stripped files is a no-op. The publish
pipeline rehydrates distributions from the canonical registry
(``synthbench.human_distributions``) when it needs them.

Usage:
    python scripts/strip-gated-distributions.py                # leaderboard-results/
    python scripts/strip-gated-distributions.py path/a.json …  # specific files
    python scripts/strip-gated-distributions.py --check        # CI guard: exit 1
                                                               # if any gated
                                                               # human_distribution
                                                               # is present
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make ``src/`` importable from a bare checkout (mirrors sibling scripts).
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from synthbench.datasets.policy import policy_for  # noqa: E402

STRIPPED_FIELDS_KEY = "stripped_fields"
STRIPPED_FIELD = "human_distribution"


def _iter_targets(paths: list[str]) -> list[Path]:
    if not paths:
        paths = [str(ROOT / "leaderboard-results")]
    out: list[Path] = []
    for p in paths:
        pth = Path(p)
        if pth.is_dir():
            out.extend(sorted(pth.glob("*.json")))
        else:
            out.append(pth)
    return out


def _is_gated(data: dict) -> bool:
    dataset = (data.get("config") or {}).get("dataset") or ""
    return bool(dataset) and policy_for(dataset).redistribution_policy == "gated"


def strip_file(path: Path, *, check_only: bool = False) -> tuple[bool, bool]:
    """Process one file. Returns ``(is_violation, was_modified)``.

    ``is_violation`` is True when the file carries gated
    ``human_distribution`` data (before stripping).
    """
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"SKIP (unreadable): {path}: {exc}", file=sys.stderr)
        return (False, False)
    if not isinstance(data, dict) or data.get("benchmark") != "synthbench":
        return (False, False)
    if not _is_gated(data):
        return (False, False)

    per_question = data.get("per_question")
    rows_with_dist = [
        q for q in (per_question or []) if isinstance(q, dict) and STRIPPED_FIELD in q
    ]
    marker = data.get(STRIPPED_FIELDS_KEY)
    marker_ok = isinstance(marker, list) and STRIPPED_FIELD in marker

    if not rows_with_dist and marker_ok:
        return (False, False)  # already stripped
    if check_only:
        return (bool(rows_with_dist), False)

    for q in rows_with_dist:
        q.pop(STRIPPED_FIELD, None)
    if not marker_ok:
        fields = set(marker) if isinstance(marker, list) else set()
        fields.add(STRIPPED_FIELD)
        data[STRIPPED_FIELDS_KEY] = sorted(fields)

    # Match the runner/report serialization (json.dump(..., indent=2), no
    # trailing newline) so stripped files stay diff-stable with fresh ones.
    path.write_text(json.dumps(data, indent=2))
    return (bool(rows_with_dist), True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        help="Result JSON files or directories (default: leaderboard-results/).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Do not modify anything; exit 1 if any gated-dataset file still "
            "carries per-question human_distribution data (CI guard)."
        ),
    )
    args = parser.parse_args()

    violations: list[Path] = []
    modified = 0
    for path in _iter_targets(args.paths):
        is_violation, was_modified = strip_file(path, check_only=args.check)
        if is_violation:
            violations.append(path)
        if was_modified:
            modified += 1

    if args.check:
        if violations:
            sample = [str(p) for p in violations[:5]]
            print(
                f"FAIL: {len(violations)} committed result file(s) carry "
                f"per-question human_distribution for a gated dataset. Run "
                f"scripts/strip-gated-distributions.py before committing. "
                f"Examples: {sample}",
                file=sys.stderr,
            )
            return 1
        print("OK: no gated human_distribution data in committed result files.")
        return 0

    print(f"Stripped gated human_distribution from {modified} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
