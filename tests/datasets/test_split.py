"""Tests for the held-out validation split (issue #259).

Covers:

* :func:`make_split` is deterministic given the same seed.
* :func:`is_held_out` agrees with the partition produced by ``make_split``.
* Held-out coverage is approximately ``held_out_frac`` for non-trivial
  inputs (statistical, with generous tolerance for small samples).
* :func:`require_held_out_auth` raises a clear, link-bearing error when
  the env var is missing.
* The runner's ``--held-out`` flag enforces the env-gate at the CLI layer.
"""

from __future__ import annotations

from click.testing import CliRunner

from synthbench.cli import main
from synthbench.datasets.split import (
    DEFAULT_HELD_OUT_FRAC,
    DEFAULT_HELD_OUT_SEED,
    HELD_OUT_AUTH_ENV,
    HeldOutAuthError,
    is_held_out,
    make_split,
    require_held_out_auth,
)


def _items(n: int) -> list[dict]:
    """Build ``n`` placeholder items with stable ids."""
    return [{"id": f"q_{i:05d}", "payload": i} for i in range(n)]


# ---------------------------------------------------------------------------
# make_split — determinism & reproducibility
# ---------------------------------------------------------------------------


def test_make_split_is_deterministic_same_seed():
    """Same seed + same items → same split, regardless of how many times we call."""
    items_a = _items(200)
    items_b = _items(200)
    public_a, held_a = make_split(items_a, seed=42)
    public_b, held_b = make_split(items_b, seed=42)
    assert [i["id"] for i in public_a] == [i["id"] for i in public_b]
    assert [i["id"] for i in held_a] == [i["id"] for i in held_b]


def test_make_split_different_seed_gives_different_split():
    """Bumping the seed reshuffles the partition (low collision probability)."""
    items_a = _items(500)
    items_b = _items(500)
    _, held_a = make_split(items_a, seed=1)
    _, held_b = make_split(items_b, seed=999_999)
    a = {i["id"] for i in held_a}
    b = {i["id"] for i in held_b}
    # Two independent ~25% subsets of 500 items should intersect on
    # roughly 25%*25%*500 ≈ 31 items. Anything wildly different (e.g. 100%
    # overlap) means the seed isn't actually changing the partition.
    overlap = a & b
    assert len(overlap) < len(a) * 0.75, (
        f"Seeds produce too-similar splits: |overlap|={len(overlap)} "
        f"of |held_a|={len(a)}"
    )


def test_make_split_order_independent():
    """Reversing the input order doesn't change which items land in held-out."""
    items_fwd = _items(300)
    items_rev = list(reversed(_items(300)))
    _, held_fwd = make_split(items_fwd, seed=DEFAULT_HELD_OUT_SEED)
    _, held_rev = make_split(items_rev, seed=DEFAULT_HELD_OUT_SEED)
    assert {i["id"] for i in held_fwd} == {i["id"] for i in held_rev}


def test_make_split_attaches_split_id():
    """Every item gets a ``_split_id`` field populated with a sha256 hex."""
    items = _items(10)
    public, held = make_split(items, seed=7)
    for item in public + held:
        sid = item.get("_split_id")
        assert isinstance(sid, str)
        assert len(sid) == 64  # full sha256 hex
        int(sid, 16)  # parseable as hex


# ---------------------------------------------------------------------------
# is_held_out — agrees with make_split
# ---------------------------------------------------------------------------


def test_is_held_out_matches_make_split():
    """``is_held_out(id, seed)`` must classify every item the same way
    ``make_split`` did, with the same seed/frac."""
    items = _items(400)
    public, held = make_split(
        items, seed=DEFAULT_HELD_OUT_SEED, held_out_frac=DEFAULT_HELD_OUT_FRAC
    )
    public_ids = {i["id"] for i in public}
    held_ids = {i["id"] for i in held}

    for iid in public_ids:
        assert not is_held_out(iid), f"{iid} in public but is_held_out=True"
    for iid in held_ids:
        assert is_held_out(iid), f"{iid} in held-out but is_held_out=False"


def test_is_held_out_seed_sensitive():
    """is_held_out's answer depends on the seed."""
    iid = "q_00001"
    answers = {is_held_out(iid, seed=s) for s in range(50)}
    # At seed=∞ the answer is a Bernoulli(0.25); across 50 different seeds
    # we should see both outcomes. If not, the seed isn't doing anything.
    assert answers == {True, False}, (
        f"is_held_out({iid!r}) doesn't depend on seed: only saw {answers}"
    )


# ---------------------------------------------------------------------------
# Coverage — ~held_out_frac of items land in held-out
# ---------------------------------------------------------------------------


def test_held_out_coverage_within_tolerance():
    """Empirical held-out fraction matches the requested fraction.

    Tolerance: ±5pp on N=1000 items. SHA-256 buckets are effectively
    uniform; 5pp gives plenty of room for sampling noise without being so
    loose that the test wouldn't catch a real off-by-half bug.
    """
    items = _items(1000)
    _, held = make_split(items, seed=DEFAULT_HELD_OUT_SEED, held_out_frac=0.25)
    frac = len(held) / len(items)
    assert 0.20 <= frac <= 0.30, f"held-out fraction {frac:.3f} outside [0.20, 0.30]"


def test_held_out_coverage_zero_and_one():
    """Boundary fractions 0.0 and 1.0 do the obvious thing."""
    items = _items(50)
    public_all, held_none = make_split(items, seed=1, held_out_frac=0.0)
    assert len(held_none) == 0
    assert len(public_all) == 50
    items2 = _items(50)
    public_none, held_all = make_split(items2, seed=1, held_out_frac=1.0)
    assert len(public_none) == 0
    assert len(held_all) == 50


# ---------------------------------------------------------------------------
# require_held_out_auth — env-gate
# ---------------------------------------------------------------------------


def test_require_held_out_auth_unset_raises():
    """No env var → clear, link-bearing error."""
    try:
        require_held_out_auth(env=[])
    except HeldOutAuthError as exc:
        msg = str(exc)
        assert HELD_OUT_AUTH_ENV in msg
        assert "259" in msg, "error should point at issue #259"
    else:
        raise AssertionError("expected HeldOutAuthError")


def test_require_held_out_auth_set_returns_value():
    """Any non-empty value passes the gate."""
    val = require_held_out_auth(env=[(HELD_OUT_AUTH_ENV, "dev-token")])
    assert val == "dev-token"


def test_require_held_out_auth_empty_string_fails():
    """Empty-string env value is treated as unset (avoids accidental bypass)."""
    try:
        require_held_out_auth(env=[(HELD_OUT_AUTH_ENV, "")])
    except HeldOutAuthError:
        pass
    else:
        raise AssertionError("expected HeldOutAuthError for empty env value")


# ---------------------------------------------------------------------------
# CLI integration — --held-out gating
# ---------------------------------------------------------------------------


def test_cli_held_out_without_auth_exits_error(monkeypatch):
    """`synthbench run --held-out` with no env var fails fast with a clear
    message and exits non-zero, before loading any provider/dataset."""
    monkeypatch.delenv(HELD_OUT_AUTH_ENV, raising=False)
    res = CliRunner().invoke(
        main,
        [
            "run",
            "--provider",
            "raw-anthropic",
            "--dataset",
            "globalopinionqa",
            "--held-out",
        ],
    )
    assert res.exit_code != 0
    out = (res.output or "") + (str(res.exception) if res.exception else "")
    assert HELD_OUT_AUTH_ENV in out
    assert "259" in out


def test_cli_held_out_with_auth_passes_gate(monkeypatch):
    """`synthbench run --held-out` with the env var set proceeds past the
    gate. We don't run a real benchmark — we just monkey-patch the async
    runner to short-circuit and assert the gate didn't trip.

    The signal we look for: the error path printed by the env-gate (issue
    #259 link) is *not* present in the output. The command may still fail
    for other reasons (provider auth, network) — that's fine, we're only
    asserting we got past the env-gate.
    """
    monkeypatch.setenv(HELD_OUT_AUTH_ENV, "dev-token")

    # Patch _run_async to a no-op so we don't actually hit a provider. The
    # gate check happens *before* asyncio.run(_run_async(...)) so by the
    # time _run_async is called, we know the gate passed.
    called = {"hit": False}

    async def fake_run_async(*args, **kwargs):
        called["hit"] = True
        return None

    monkeypatch.setattr("synthbench.cli._run_async", fake_run_async)

    res = CliRunner().invoke(
        main,
        [
            "run",
            "--provider",
            "raw-anthropic",
            "--dataset",
            "globalopinionqa",
            "--held-out",
        ],
    )
    # We should have reached _run_async, which means the gate passed.
    assert called["hit"], (
        f"--held-out with auth set did not pass gate: exit={res.exit_code} "
        f"output={res.output!r} exc={res.exception!r}"
    )
    # And the gate error message must NOT appear.
    out = res.output or ""
    assert "Held-out evaluation requires the" not in out
