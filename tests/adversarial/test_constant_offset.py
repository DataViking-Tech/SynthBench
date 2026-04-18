"""Adversarial tests for :code:`ANOMALY_CONSTANT_OFFSET` (sb-n2tz).

The constant-offset attack is ``model[opt] = human[opt] + c`` renormalized.
Because the transformation is strictly monotonic, the option rank order
is preserved on every question — per-question ``kendall_tau == 1.0``
uniformly. Real LLM sampling flips minor ranks on nearly-tied options.

The detector's fingerprint: a submission where ``>= 95%`` of questions
have near-unity ``kendall_tau`` over ``n >= 25``. Across every real
submission in ``leaderboard-results/`` this share tops out at ~26%.

These tests assert both directions:

* The adversarial ``constant_offset.json`` fixture fires the detector at
  ERROR severity.
* Real leaderboard submissions across multiple providers/datasets do not
  trip it — regression guard against threshold drift.

Doc reference: ``docs/benchmark-hardening-analysis.md §3.3``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthbench.anomaly import (
    CONSTANT_OFFSET_MIN_N,
    CONSTANT_OFFSET_PERFECT_TAU_FRACTION,
    check_constant_offset,
)
from synthbench.validation import Severity, validate_file

FIXTURES = Path(__file__).resolve().parent / "fixtures"
LEADERBOARD = Path(__file__).resolve().parents[2] / "leaderboard-results"


def test_constant_offset_fixture_fails_with_error() -> None:
    """The ``constant_offset.json`` fixture must produce an ERROR-severity
    ``ANOMALY_CONSTANT_OFFSET`` issue and the overall validation must
    fail. Acceptance criterion for sb-n2tz.
    """
    path = FIXTURES / "constant_offset.json"
    assert path.is_file(), f"fixture missing: {path}"

    report = validate_file(path, tier1=True, tier2=True, tier3=True)

    offset_issues = [i for i in report.issues if i.code == "ANOMALY_CONSTANT_OFFSET"]
    assert len(offset_issues) == 1, (
        f"expected exactly one ANOMALY_CONSTANT_OFFSET issue, got "
        f"{[(i.code, i.severity.value) for i in report.issues]}"
    )
    assert offset_issues[0].severity is Severity.ERROR
    assert not report.ok, "constant_offset fixture must fail validation overall"


def test_detector_silent_on_legitimate_baselines() -> None:
    """Uniform (null-agent) and raw-response-desync fixtures cover the
    cases where the validator *must* pass (null_agent) or where a
    different detector is the intended trigger. Neither has near-unity
    tau; both must leave the constant-offset detector silent so we don't
    regress onto legitimate baselines.
    """
    for name in ("null_agent", "raw_response_desync", "lied_aggregate"):
        data = json.loads((FIXTURES / f"{name}.json").read_text())
        issue = check_constant_offset(data.get("per_question", []))
        assert issue is None, (
            f"{name}: constant-offset detector fired on a fixture whose "
            f"attack is unrelated to monotonic-transformation. Message: "
            f"{issue.message if issue else ''}"
        )


def test_returns_none_below_min_sample_size() -> None:
    """Sub-``CONSTANT_OFFSET_MIN_N`` samples must short-circuit to
    ``None`` even when every tau is 1.0. Below the minimum the tau
    ratio is not a reliable signal (a 5-question debug fixture could
    easily hit 100% perfect tau by coincidence).
    """
    tiny = [
        {"kendall_tau": 1.0, "jsd": 0.001, "key": f"k{i}"}
        for i in range(CONSTANT_OFFSET_MIN_N - 1)
    ]
    assert check_constant_offset(tiny) is None


@pytest.mark.parametrize(
    "provider_match",
    [
        "claude-haiku-4-5",
        "claude-sonnet-4",
        "gpt-4o-mini",
        "gemini-2.5-flash",
        "llama-3.3-70b",
        "majority-baseline",
        "random-baseline",
        "ensemble_3blend",
    ],
)
def test_real_submissions_not_flagged(provider_match: str) -> None:
    """Real submissions must not trip the detector. If this ever fires,
    either the ``CONSTANT_OFFSET_PERFECT_TAU_FRACTION`` threshold
    drifted too low or the detector's tau-counting logic regressed.
    """
    if not LEADERBOARD.is_dir():
        pytest.skip("leaderboard-results/ not present in this worktree")

    matches = sorted(LEADERBOARD.glob(f"*{provider_match}*.json"))
    if not matches:
        pytest.skip(f"no leaderboard fixture matching {provider_match}")

    flagged: list[tuple[str, str]] = []
    for path in matches:
        data = json.loads(path.read_text())
        if data.get("benchmark") != "synthbench":
            continue
        issue = check_constant_offset(data.get("per_question") or [])
        if issue is not None:
            flagged.append((path.name, issue.message))

    assert not flagged, (
        f"real submissions for {provider_match} tripped "
        f"ANOMALY_CONSTANT_OFFSET (threshold "
        f"{CONSTANT_OFFSET_PERFECT_TAU_FRACTION:.0%}): {flagged}"
    )
