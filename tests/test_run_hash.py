"""Tests for `synthbench.run_hash.compute_run_hash` (refs sb-1ix, GH#256).

The hash is a tamper-detection primitive — these tests pin the
canonicalization rules so a future refactor cannot silently change the
hash space and break already-submitted leaderboard rows.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from synthbench.run_hash import compute_run_hash


def _adapter() -> dict[str, str]:
    return {
        "name": "acme/test",
        "version": "1.0.0",
        "vendor": "acme-ai",
        "vendor_version": "2026.05.14",
    }


def _suite() -> dict[str, object]:
    return {
        "keys": ["Q_001", "Q_002", "Q_003"],
        "n_keys": 3,
        "version": "0.1.0",
    }


def _raw_response(qkey: str, pid: str, text: str) -> dict[str, str]:
    return {"question_key": qkey, "persona_id": pid, "raw_text": text}


def test_returns_64_char_lowercase_hex():
    """The hash is documented as a bare sha256 hex digest — vendor CI
    will regex-match it, so the shape must not drift."""
    h = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1"],
        raw_responses=[_raw_response("Q_001", "p1", "yes")],
    )
    assert len(h) == 64
    assert h == h.lower()
    int(h, 16)  # raises if not valid hex


def test_deterministic_across_calls():
    """Same inputs → same hash, full stop. This is the core integrity
    property a tampered-submission detector relies on."""
    args = dict(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1", "p2"],
        raw_responses=[
            _raw_response("Q_001", "p1", "yes"),
            _raw_response("Q_002", "p2", "no"),
        ],
    )
    assert compute_run_hash(**args) == compute_run_hash(**args)


def test_raw_response_traversal_order_does_not_affect_hash():
    """The harness iterates (question, persona) in an order that is an
    implementation detail; the hash must depend on the *set* of samples,
    not the traversal order. We sort by (question_key, persona_id) before
    hashing to enforce this."""
    rrs_a = [
        _raw_response("Q_001", "p1", "yes"),
        _raw_response("Q_002", "p2", "no"),
        _raw_response("Q_001", "p2", "maybe"),
    ]
    rrs_b = list(reversed(rrs_a))
    h_a = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1", "p2"],
        raw_responses=rrs_a,
    )
    h_b = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1", "p2"],
        raw_responses=rrs_b,
    )
    assert h_a == h_b


def test_persona_seed_order_affects_hash():
    """Persona seed *order* is part of the run identity — the harness
    feeds personas in a specific sequence, and a different sequence is
    a different run. Distinct from raw_responses order, which is just
    traversal noise."""
    h1 = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1", "p2"],
        raw_responses=[],
    )
    h2 = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p2", "p1"],
        raw_responses=[],
    )
    assert h1 != h2


def test_suite_key_order_does_not_affect_hash():
    """The suite manifest's ``keys`` list is the set of question keys;
    a suite file with the same keys in a different order is the same
    suite. We sort before hashing."""
    suite_a = {"keys": ["Q_002", "Q_001", "Q_003"], "n_keys": 3, "version": "0.1.0"}
    suite_b = {"keys": ["Q_001", "Q_002", "Q_003"], "n_keys": 3, "version": "0.1.0"}
    h_a = compute_run_hash(
        adapter=_adapter(), suite=suite_a, persona_seeds=[], raw_responses=[]
    )
    h_b = compute_run_hash(
        adapter=_adapter(), suite=suite_b, persona_seeds=[], raw_responses=[]
    )
    assert h_a == h_b


def test_raw_text_change_changes_hash():
    """Tampered raw_text → different hash. This is the leaderboard CI's
    primary detection signal."""
    base = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1"],
        raw_responses=[_raw_response("Q_001", "p1", "yes")],
    )
    tampered = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1"],
        raw_responses=[_raw_response("Q_001", "p1", "no")],
    )
    assert base != tampered


def test_adapter_field_change_changes_hash():
    """Two vendors with literally the same adapter code but different
    vendor strings must hash differently — the leaderboard distinguishes
    submissions, not adapters."""
    a1 = _adapter()
    a2 = {**a1, "vendor": "different-co"}
    h1 = compute_run_hash(
        adapter=a1, suite=_suite(), persona_seeds=[], raw_responses=[]
    )
    h2 = compute_run_hash(
        adapter=a2, suite=_suite(), persona_seeds=[], raw_responses=[]
    )
    assert h1 != h2


def test_suite_version_change_changes_hash():
    """A submission against ``core@0.1.0`` and ``core@0.2.0`` are not
    the same submission, even if the keys happen to overlap exactly."""
    s1 = _suite()
    s2 = {**s1, "version": "0.2.0"}
    h1 = compute_run_hash(
        adapter=_adapter(), suite=s1, persona_seeds=[], raw_responses=[]
    )
    h2 = compute_run_hash(
        adapter=_adapter(), suite=s2, persona_seeds=[], raw_responses=[]
    )
    assert h1 != h2


def test_extra_adapter_fields_are_ignored():
    """Vendors will inevitably attach diagnostic fields (commit_sha,
    build_id, etc). Those must not invalidate the hash, otherwise old
    leaderboard rows break the moment a vendor adds telemetry."""
    base = _adapter()
    extended = {**base, "commit_sha": "deadbeef", "build_id": 42}
    h_base = compute_run_hash(
        adapter=base, suite=_suite(), persona_seeds=[], raw_responses=[]
    )
    h_ext = compute_run_hash(
        adapter=extended, suite=_suite(), persona_seeds=[], raw_responses=[]
    )
    assert h_base == h_ext


def test_extra_raw_response_fields_are_ignored():
    """Same principle as adapter extras — a sample's ``latency_ms`` or
    ``provider_request_id`` is metadata, not identity."""
    base = [_raw_response("Q_001", "p1", "yes")]
    extended = [{**base[0], "latency_ms": 123, "request_id": "abc"}]
    h_base = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1"],
        raw_responses=base,
    )
    h_ext = compute_run_hash(
        adapter=_adapter(),
        suite=_suite(),
        persona_seeds=["p1"],
        raw_responses=extended,
    )
    assert h_base == h_ext


def test_missing_adapter_field_raises():
    """Identity fields are load-bearing — a missing one must fail loudly
    rather than silently hashing a partial identity."""
    bad = {k: v for k, v in _adapter().items() if k != "vendor"}
    with pytest.raises(ValueError, match="adapter missing"):
        compute_run_hash(
            adapter=bad, suite=_suite(), persona_seeds=[], raw_responses=[]
        )


def test_missing_suite_field_raises():
    bad = {"keys": ["Q_001"], "n_keys": 1}  # no version
    with pytest.raises(ValueError, match="suite missing"):
        compute_run_hash(
            adapter=_adapter(), suite=bad, persona_seeds=[], raw_responses=[]
        )


def test_missing_raw_response_field_raises():
    bad = [{"question_key": "Q_001", "persona_id": "p1"}]  # no raw_text
    with pytest.raises(ValueError, match=r"raw_responses\[0\] missing"):
        compute_run_hash(
            adapter=_adapter(),
            suite=_suite(),
            persona_seeds=["p1"],
            raw_responses=bad,
        )


def test_canonical_json_format_is_used():
    """The hash inputs go through ``json.dumps(sort_keys=True,
    separators=(",", ":"))`` — verify by reconstructing the expected
    digest from a known payload. Pinning this means a future refactor
    that swaps the JSON encoder (e.g. to ``json.dumps`` defaults with
    spaces) will be caught instead of silently re-hashing the world."""
    adapter = _adapter()
    suite = _suite()
    expected_payload = {
        "adapter": {
            "name": "acme/test",
            "version": "1.0.0",
            "vendor": "acme-ai",
            "vendor_version": "2026.05.14",
        },
        "suite": {
            "keys": ["Q_001", "Q_002", "Q_003"],
            "n_keys": 3,
            "version": "0.1.0",
        },
        "persona_seeds": [],
        "raw_responses": [],
    }
    expected = hashlib.sha256(
        json.dumps(expected_payload, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    actual = compute_run_hash(
        adapter=adapter, suite=suite, persona_seeds=[], raw_responses=[]
    )
    assert actual == expected
