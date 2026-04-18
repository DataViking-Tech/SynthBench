"""Adversarial fixtures that MUST fail validation.

Scaffolded by sb-0rvy with the first fabrication: ``public_copy_fake_private``.
sb-5xfk expands this into the full 8-fixture suite from
``docs/benchmark-hardening-analysis.md`` §5.
"""

from __future__ import annotations

import json
from pathlib import Path

from synthbench.validation import (
    Severity,
    _validate_private_holdout,
)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text())


class TestPublicCopyFakePrivate:
    """Attack: copy public human distributions; sample private from marginal.

    The fake-private rows diverge from the true per-question private
    distribution, so the SPS gap is large. At production-scale split sizes
    (n_public=200, n_private=60) the divergence must surface as an ERROR —
    not a WARNING — per the sb-0rvy promotion.
    """

    def test_fires_holdout_divergence_as_error(self):
        data = _load("public_copy_fake_private.json")
        issues = _validate_private_holdout(data)
        divergence = [i for i in issues if i.code == "HOLDOUT_DIVERGENCE"]
        assert divergence, "adversarial fixture should trip HOLDOUT_DIVERGENCE"
        assert divergence[0].severity is Severity.ERROR, (
            "HOLDOUT_DIVERGENCE must be ERROR when min_side >= 50 "
            f"(got {divergence[0].severity})"
        )

    def test_fixture_meets_min_side_precondition(self):
        """Guardrail: if the fixture ever drops below min_side=50, the ERROR
        path isn't the one we're exercising."""
        data = _load("public_copy_fake_private.json")
        from synthbench.private_holdout import compute_split_sps

        split = compute_split_sps(data["config"]["dataset"], data["per_question"])
        assert split["n_public"] >= 50
        assert split["n_private"] >= 50
