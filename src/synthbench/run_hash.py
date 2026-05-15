"""Content-addressed run hash for vendor submissions (refs sb-1ix, GH#256).

A run hash uniquely identifies a SynthBench vendor submission. It is the
sha256 of canonical JSON (sorted keys, no whitespace) over the four
inputs that determine a submission's contents:

  1. adapter identity: ``{name, version, vendor, vendor_version}``
  2. suite manifest:   ``{keys, n_keys, version}`` from ``suites/<suite>.json``
  3. persona seeds:    the ordered persona ids / seeds the harness iterated
  4. raw responses:    list of ``{question_key, persona_id, raw_text}``
                       samples produced by the adapter

Leaderboard CI uses this to detect tampered submissions: rebuild the
hash from ``raw_responses`` on the submitted ``run.json`` and compare
against the stored ``run_hash``. Two runs of a deterministic adapter
against the same suite + persona seeds MUST produce the same hash.

Hashing rules (kept here so the spec lives next to the implementation):

* JSON is dumped with ``sort_keys=True, separators=(",", ":")`` so
  byte-for-byte output is deterministic.
* The suite ``keys`` list is sorted before hashing — suite identity is
  the *set* of question keys plus version, not the iteration order.
* The ``raw_responses`` list is sorted by ``(question_key, persona_id)``
  so the hash is independent of the harness's traversal order, but each
  sample's ``raw_text`` is kept verbatim.
* Extra fields on the adapter / suite / sample dicts are *ignored*. This
  lets vendors attach diagnostic metadata without invalidating hashes.
* All values are coerced to ``str`` (except ``suite.n_keys`` which is
  ``int``) so callers cannot accidentally make a hash depend on whether
  a field arrived as ``"0.1.0"`` vs an integer ``1``.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

_ADAPTER_FIELDS = ("name", "version", "vendor", "vendor_version")
_SUITE_FIELDS = ("keys", "n_keys", "version")
_RAW_RESPONSE_FIELDS = ("question_key", "persona_id", "raw_text")


def compute_run_hash(
    *,
    adapter: Mapping[str, Any],
    suite: Mapping[str, Any],
    persona_seeds: Sequence[Any],
    raw_responses: Sequence[Mapping[str, Any]],
) -> str:
    """Compute the content-addressed run hash for a submission.

    Args:
        adapter: must carry keys ``name``, ``version``, ``vendor``,
            ``vendor_version``. Extra fields are ignored.
        suite: must carry keys ``keys`` (list[str]), ``n_keys`` (int),
            and ``version`` (str). Typically loaded from
            ``suites/<suite>.json``.
        persona_seeds: ordered persona ids / seeds, exactly as the
            harness iterated them. Order is preserved in the hash.
        raw_responses: list of ``{question_key, persona_id, raw_text}``
            samples. Re-sorted into canonical order before hashing.

    Returns:
        Lowercase sha256 hex digest (64 chars), no prefix.

    Raises:
        ValueError: if any required field is missing on adapter, suite,
            or an individual raw_responses entry.
    """
    payload = {
        "adapter": _canonicalize_adapter(adapter),
        "suite": _canonicalize_suite(suite),
        "persona_seeds": [str(s) for s in persona_seeds],
        "raw_responses": _canonicalize_raw_responses(raw_responses),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _canonicalize_adapter(adapter: Mapping[str, Any]) -> dict[str, str]:
    missing = [k for k in _ADAPTER_FIELDS if k not in adapter]
    if missing:
        raise ValueError(f"adapter missing required fields: {missing}")
    return {k: str(adapter[k]) for k in _ADAPTER_FIELDS}


def _canonicalize_suite(suite: Mapping[str, Any]) -> dict[str, Any]:
    missing = [k for k in _SUITE_FIELDS if k not in suite]
    if missing:
        raise ValueError(f"suite missing required fields: {missing}")
    keys = sorted(str(k) for k in suite["keys"])
    return {
        "keys": keys,
        "n_keys": int(suite["n_keys"]),
        "version": str(suite["version"]),
    }


def _canonicalize_raw_responses(
    raw_responses: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for idx, sample in enumerate(raw_responses):
        missing = [k for k in _RAW_RESPONSE_FIELDS if k not in sample]
        if missing:
            raise ValueError(f"raw_responses[{idx}] missing required fields: {missing}")
        rows.append({k: str(sample[k]) for k in _RAW_RESPONSE_FIELDS})
    rows.sort(key=lambda r: (r["question_key"], r["persona_id"]))
    return rows
