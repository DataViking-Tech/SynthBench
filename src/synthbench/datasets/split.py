"""Held-out validation split for SynthBench eval datasets.

This module implements the **deterministic public / held-out partition** that
backs the "private leaderboard" half of the integrity work tracked in
GitHub issue #259. It is intentionally narrow in scope: the function pair
:func:`make_split` / :func:`is_held_out` operates on already-loaded items
(``list[dict]``) so it composes with the existing dataset adapters (Pew ATP,
GlobalOpinionQA) without changing how those datasets are downloaded or
parsed.

There is a sibling module — :mod:`synthbench.private_holdout` — that solves a
related but different problem: it provides a per-``(dataset, key)`` private
suffix used by the *publish* pipeline to compute cheat-detector SPS deltas on
shipped artifacts. That module is wired into ``compute_split_sps`` and the
leaderboard's anti-fabrication gate. The split implemented *here* is the
runner-side filter: when a contributor invokes ``synthbench run --held-out``,
we use :func:`is_held_out` to decide which loaded items count toward the
score for that run. The two modules deliberately share a hashing approach
(SHA-256, integer-bucket, dataset-scoped) so a future refactor can unify
them, but for now we keep them separate to avoid disturbing the
already-shipped publish path (see ``private_holdout.HOLDOUT_ENABLED_DATASETS``
for the per-dataset fractions baked into shipped leaderboard rows).

Design choices
--------------

* **Deterministic + seeded.** The split is keyed off the item's stable id
  (``item["id"]`` / ``item["key"]`` / fallback ``item["question_id"]``) and a
  caller-supplied integer ``seed``. The same ``(id, seed)`` pair always
  produces the same partition decision, irrespective of input order or
  Python version.
* **Order-independent.** Items are bucketed by ``sha256(id + ":" + seed)``,
  not by index. Re-ordering ``items`` does not change the split.
* **Distribution gate via env var.** The raw data values are *not* in this
  module — adapters download them on demand into the user's data dir. So we
  cannot solve "don't ship held-out data in the wheel" by excluding files
  from the package; instead, we gate held-out evaluation behind
  ``SYNTHBENCH_HELD_OUT_AUTH``. The CLI surface (``cli.py``) enforces the
  env-gate before this module is even called; this module re-validates as a
  belt-and-suspenders defence against direct library use.

Surface
-------

* :func:`make_split` — split a loaded item list into ``(public, held_out)``.
* :func:`is_held_out` — fast O(1) classification of a single item id.
* :data:`DEFAULT_HELD_OUT_SEED` — the canonical seed used by the runner.
* :data:`DEFAULT_HELD_OUT_FRAC` — 25%, matching the issue brief.
* :data:`HELD_OUT_AUTH_ENV` — env var name the runner checks.

See ``docs/held-out.md`` for the contributor-facing explainer.
"""

from __future__ import annotations

import hashlib
import os
from typing import Iterable

# Canonical default seed for the held-out split. Pinned so the partition is
# stable across releases — bumping this value is a breaking change because it
# reshuffles which questions are public vs. held-out and invalidates all
# previously-scored held-out runs. The specific value is arbitrary (it is
# `int("synthbench-held-out-v1"[:8].encode().hex(), 16) % (2**31)` style — a
# stable string-derived integer with no other meaning).
DEFAULT_HELD_OUT_SEED: int = 0x53594E54  # "SYNT" — stable, arbitrary.

# Default held-out fraction. The issue spec asks for 25%; this matches the
# upper end of the public-vs-held-out range floated in #259 (20-30%).
DEFAULT_HELD_OUT_FRAC: float = 0.25

# Integer modulus for the bucket comparison. Using a large prime-adjacent
# integer rather than e.g. 100 keeps the threshold continuous in
# ``held_out_frac`` for fractional inputs like 0.237 without rounding to the
# nearest percent.
_BUCKET_MOD: int = 10_000_000

# Env var name. The runner refuses ``--held-out`` runs unless this is set
# (to any non-empty value). It is a placeholder for a future shared-secret
# gate: in production, the leaderboard server will issue rotating tokens to
# the periodic re-eval workers. For local development, contributors can set
# it to any non-empty string.
HELD_OUT_AUTH_ENV: str = "SYNTHBENCH_HELD_OUT_AUTH"

# Datasets to which the runner-side held-out filter applies. Keeping this an
# explicit allow-list (rather than splitting *every* dataset by default)
# preserves backward compatibility with shipped leaderboard rows for the
# other datasets — see ``docs/held-out.md`` § "Migration & shipped scores".
# The two datasets called out in issue #259 are Pew ATP (which ships in
# SynthBench as ``pewtech``) and GlobalOpinionQA.
HELD_OUT_ENABLED_DATASETS: frozenset[str] = frozenset(
    {
        "pewtech",
        "globalopinionqa",
    }
)


def is_held_out_enabled_dataset(dataset_name: str) -> bool:
    """Return True iff ``dataset_name`` participates in the runner-side split.

    Datasets outside :data:`HELD_OUT_ENABLED_DATASETS` are not affected by
    the ``--held-out`` flag and keep their pre-#259 "all items" default.
    """
    return dataset_name in HELD_OUT_ENABLED_DATASETS


class HeldOutAuthError(RuntimeError):
    """Raised when held-out evaluation is requested without the auth env var.

    The error message points at GitHub issue #259 so a developer hitting it
    locally has an obvious next step.
    """


def _coerce_id(item: dict) -> str:
    """Best-effort extraction of a stable identifier from a loaded item dict.

    The eval datasets here use different conventions: Pew ATP items tend to
    carry ``id`` / ``question_id``; GlobalOpinionQA items use ``key``. We try
    each in turn rather than forcing a normalisation pass at the adapter
    layer, because doing the latter would mean touching every dataset
    adapter for what is otherwise a pure filter.

    Raises ``ValueError`` if no usable id field is present — splitting items
    without stable ids is meaningless (you'd get a different partition on
    each invocation), so we fail loudly rather than silently fall back to
    e.g. ``str(item)``.
    """
    for field in ("id", "key", "question_id"):
        val = item.get(field)
        if isinstance(val, (str, int)) and str(val).strip():
            return str(val)
    raise ValueError(
        "Item is missing a stable identifier (expected one of "
        "'id', 'key', or 'question_id'): " + repr(item)[:200]
    )


def _bucket(item_id: str, seed: int) -> int:
    """Hash ``(id, seed)`` into ``[0, _BUCKET_MOD)``.

    SHA-256 on a fixed ASCII encoding gives us cross-Python-version
    stability. We slice 8 hex chars (32 bits) before the modulus because
    that's more than enough entropy for any plausible per-dataset item
    count and keeps the hashing cheap.
    """
    digest = hashlib.sha256(f"{item_id}:{seed}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % _BUCKET_MOD


def _threshold(held_out_frac: float) -> int:
    """Integer threshold corresponding to ``held_out_frac``.

    Items whose bucket is strictly less than the threshold are held-out.
    """
    if not 0.0 <= held_out_frac <= 1.0:
        raise ValueError(f"held_out_frac must be in [0, 1], got {held_out_frac!r}")
    return int(round(held_out_frac * _BUCKET_MOD))


def is_held_out(
    item_id: str,
    seed: int = DEFAULT_HELD_OUT_SEED,
    held_out_frac: float = DEFAULT_HELD_OUT_FRAC,
) -> bool:
    """Return ``True`` if the given item id is in the held-out partition.

    Cheap O(1) lookup that mirrors the partition computed by
    :func:`make_split`. Useful at evaluation time when the runner has a
    single item id and wants to skip the cost of building two lists.

    Args:
        item_id: Stable id of the item (see :func:`_coerce_id` for the
            field-resolution policy when working with a dict).
        seed: Integer seed pinning the partition. Defaults to
            :data:`DEFAULT_HELD_OUT_SEED`.
        held_out_frac: Fraction in ``[0, 1]`` of items to mark held-out.
            Defaults to :data:`DEFAULT_HELD_OUT_FRAC` (25%).

    Returns:
        ``True`` iff the item lands in the held-out bucket.
    """
    return _bucket(item_id, seed) < _threshold(held_out_frac)


def make_split(
    items: list[dict],
    seed: int = DEFAULT_HELD_OUT_SEED,
    held_out_frac: float = DEFAULT_HELD_OUT_FRAC,
) -> tuple[list[dict], list[dict]]:
    """Partition ``items`` into ``(public, held_out)`` deterministically.

    Each item gains a ``_split_id`` field (the SHA-256 hex of
    ``f"{id}:{seed}"``) so downstream code can recover the bucket without
    re-hashing. The decision is ``int(_split_id[:8], 16) % _BUCKET_MOD <
    threshold`` — i.e. identical to :func:`is_held_out`.

    The function is **non-mutating** at the list level (it returns two new
    lists) but **does** add the ``_split_id`` key to the dicts themselves.
    Items that already carry a ``_split_id`` get it overwritten — we treat
    that field as owned by this module.

    Args:
        items: List of item dicts. Each must carry an ``id`` / ``key`` /
            ``question_id`` field; see :func:`_coerce_id`.
        seed: Integer seed pinning the partition.
        held_out_frac: Fraction in ``[0, 1]`` to assign to held-out.

    Returns:
        ``(public_items, held_out_items)``. The relative order of items
        within each list matches the input order.

    Raises:
        ValueError: An item is missing a stable id field, or
            ``held_out_frac`` is out of range.
    """
    threshold = _threshold(held_out_frac)
    public: list[dict] = []
    held_out: list[dict] = []
    for item in items:
        item_id = _coerce_id(item)
        digest = hashlib.sha256(f"{item_id}:{seed}".encode("utf-8")).hexdigest()
        item["_split_id"] = digest
        bucket = int(digest[:8], 16) % _BUCKET_MOD
        if bucket < threshold:
            held_out.append(item)
        else:
            public.append(item)
    return public, held_out


def require_held_out_auth(
    env: Iterable[tuple[str, str]] | None = None,
) -> str:
    """Validate that ``SYNTHBENCH_HELD_OUT_AUTH`` is set.

    Returns the env value on success; raises :class:`HeldOutAuthError` with
    a clear, link-bearing message on failure. Splitting this out of the CLI
    layer lets library callers (e.g. notebook research code) get the same
    gate enforcement and the same error message.

    Args:
        env: Optional iterable of ``(key, value)`` pairs to use instead of
            :data:`os.environ`. Lets tests inject without touching the
            global process environment.
    """
    if env is None:
        value = os.environ.get(HELD_OUT_AUTH_ENV, "")
    else:
        value = dict(env).get(HELD_OUT_AUTH_ENV, "")
    if not value:
        raise HeldOutAuthError(
            "Held-out evaluation requires the "
            f"{HELD_OUT_AUTH_ENV} environment variable to be set.\n"
            "This is a placeholder for the future shared-secret gate that "
            "protects the held-out validation cut from accidental leak in "
            "distributed installs. For local development you may set it to "
            "any non-empty value.\n"
            "See https://github.com/DataViking-Tech/SynthBench/issues/259 "
            "for context."
        )
    return value


__all__ = [
    "DEFAULT_HELD_OUT_FRAC",
    "DEFAULT_HELD_OUT_SEED",
    "HELD_OUT_AUTH_ENV",
    "HELD_OUT_ENABLED_DATASETS",
    "HeldOutAuthError",
    "is_held_out",
    "is_held_out_enabled_dataset",
    "make_split",
    "require_held_out_auth",
]
