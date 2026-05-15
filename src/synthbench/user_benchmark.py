"""User-contributed benchmark dataset artifact (sb-7je / Move 6).

A *user benchmark* is a community-contributed dataset of survey questions
with ground-truth human response distributions. It is the *dataset twin* of
:mod:`synthbench.user_config` — where a user-config publishes how a vendor
was tuned for a subgroup, a user-benchmark publishes the questions the
leaderboard should score against. The Round-2 PMF read flagged
domain-specificity (healthcare, fintech, product behaviour, NPS) as the
universal "but" against the default Pew/GlobalOpinionQA backbone; rather
than ship vertical packs ourselves, we open a submission flow so the
community contributes them.

This module is the schema + validator + canonical-hash for that artifact.
The CLI calls :func:`load_benchmark_file` to read a JSON file,
:func:`validate_benchmark` to enforce the schema, and
:func:`attach_to_submission_body` to stamp the benchmark block (plus its
content hash) onto a run JSON before it goes to ``POST /submit``.

The submission body grows one new top-level key, ``user_benchmark``,
carrying the canonical dict including a SHA-256 ``benchmark_hash`` computed
from the ``questions`` block. We keep it top-level (not inside ``config``)
for the same reason as ``user_config``: the existing canonical ``config_id``
hash reads a fixed set of ``config`` keys, and we must not perturb it. The
new leaderboard slice identity is the ``benchmark_id``, distinct from the
default ``opinionsqa``/``globalopinionqa`` slices.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from synthbench import __version__

# Top-level keys we serialise into the submission body in a stable order.
# Anything not in this set is rejected at validation time so contributors
# can't smuggle opaque fields past the leaderboard.
_ALLOWED_KEYS: tuple[str, ...] = (
    "benchmark_id",
    "title",
    "contributor",
    "description",
    "domain",
    "harness_version",
    "source",
    "redistribution_policy",
    "questions",
    "notes",
)

# kebab-case ASCII slugs so ``benchmark_id`` and ``domain`` slot cleanly
# into URL path segments and filesystem paths.
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$")

_HANDLE_RE = re.compile(r"^@[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Must mirror :data:`synthbench.datasets.base.RedistributionPolicy`. We
# duplicate the enum locally instead of importing it so the validator
# stays cheap to load (datasets/__init__ pulls in adapter code).
_REDIST_POLICIES: frozenset[str] = frozenset(
    {"full", "gated", "aggregates_only", "citation_only"}
)

# Minimum question count to be worth running. Lower than this and the
# scoring noise drowns out any signal — Round-2 PMF respondents specifically
# called out "tiny custom decks" as a failure mode.
_MIN_QUESTIONS = 5

# Distribution mass must sum within this tolerance of 1.0. Same slack as
# the in-tree Question dataclass uses before it renormalises.
_DIST_TOLERANCE = 0.01


@dataclass
class BenchmarkError:
    """Structured validation failure. ``field`` is a dotted path so the CLI
    can print actionable lines: ``questions[3].human_distribution`` instead
    of "somewhere in the questions list".
    """

    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}" if self.field else self.message


@dataclass
class UserBenchmark:
    """Parsed-and-validated dataset artifact, ready to embed in a submission.

    ``raw`` keeps the canonicalised dict (key order normalised, no
    ``benchmark_hash`` yet — that gets computed at attachment time) so the
    caller can attach it verbatim without re-serialising through the
    dataclass layer.
    """

    benchmark_id: str
    title: str
    contributor: str
    domain: str
    harness_version: str
    redistribution_policy: str
    n_questions: int
    raw: dict[str, Any]

    @property
    def leaderboard_slice_key(self) -> str:
        """Identifier the leaderboard uses to group results scored against
        this benchmark. The ``benchmark_id`` alone — slices are global,
        not per-contributor, so two contributors who submit the same id
        collide deliberately (the server resolves the collision against
        the content hash)."""
        return self.benchmark_id


# --- Loading -----------------------------------------------------------------


def load_benchmark_file(
    path: Union[str, Path],
) -> Union[dict[str, Any], BenchmarkError]:
    """Read a JSON benchmark file from disk and return its parsed dict.

    Returns a :class:`BenchmarkError` for IO failures, malformed JSON, or a
    document that doesn't parse to a mapping. The caller is expected to
    pipe the dict through :func:`validate_benchmark` before trusting any
    field.
    """
    p = Path(path)
    try:
        text = p.read_text()
    except OSError as exc:
        return BenchmarkError(field="", message=f"cannot read {p}: {exc}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return BenchmarkError(field="", message=f"{p}: invalid JSON: {exc}")
    if not isinstance(data, dict):
        return BenchmarkError(
            field="",
            message=f"{p}: top-level JSON must be an object, got {type(data).__name__}",
        )
    return data


# --- Validation --------------------------------------------------------------


def _check_str(data: dict, key: str, errors: list[BenchmarkError]) -> Optional[str]:
    val = data.get(key)
    if not isinstance(val, str) or not val.strip():
        errors.append(BenchmarkError(key, "required non-empty string"))
        return None
    return val.strip()


def _check_slug(value: Optional[str], field: str, errors: list[BenchmarkError]) -> None:
    if value is None:
        return
    if not _SLUG_RE.match(value):
        errors.append(
            BenchmarkError(
                field,
                "must be kebab-case ASCII slug: lowercase letters, digits, "
                "and internal hyphens, 2-64 chars",
            )
        )


def _check_contributor(value: Optional[str], errors: list[BenchmarkError]) -> None:
    if value is None:
        return
    if _HANDLE_RE.match(value) or _EMAIL_RE.match(value):
        return
    errors.append(
        BenchmarkError(
            "contributor",
            "must be a GitHub-style @handle or a bare email address",
        )
    )


def _check_source(data: dict, errors: list[BenchmarkError]) -> None:
    src = data.get("source")
    if src is None:
        errors.append(BenchmarkError("source", "required"))
        return
    if not isinstance(src, dict):
        errors.append(BenchmarkError("source", "must be a mapping"))
        return
    citation = src.get("citation")
    if not isinstance(citation, str) or not citation.strip():
        errors.append(BenchmarkError("source.citation", "required non-empty string"))
    license_ = src.get("license")
    if not isinstance(license_, str) or not license_.strip():
        errors.append(BenchmarkError("source.license", "required non-empty string"))
    url = src.get("url")
    if url is not None and (not isinstance(url, str) or not url.strip()):
        errors.append(BenchmarkError("source.url", "must be a non-empty string if set"))
    allowed = {"citation", "license", "url"}
    extra = sorted(set(src) - allowed)
    if extra:
        errors.append(
            BenchmarkError(
                "source",
                f"unknown keys: {', '.join(extra)}. Allowed: {', '.join(sorted(allowed))}",
            )
        )


def _check_redistribution(data: dict, errors: list[BenchmarkError]) -> None:
    policy = data.get("redistribution_policy")
    if policy is None:
        errors.append(BenchmarkError("redistribution_policy", "required"))
        return
    if policy not in _REDIST_POLICIES:
        errors.append(
            BenchmarkError(
                "redistribution_policy",
                f"must be one of {sorted(_REDIST_POLICIES)}; got {policy!r}",
            )
        )


def _check_question(
    q: Any, index: int, seen_keys: set[str], errors: list[BenchmarkError]
) -> None:
    prefix = f"questions[{index}]"
    if not isinstance(q, dict):
        errors.append(BenchmarkError(prefix, "must be a mapping"))
        return

    allowed = {"key", "text", "options", "human_distribution", "topic"}
    extra = sorted(set(q) - allowed)
    if extra:
        errors.append(
            BenchmarkError(
                prefix,
                f"unknown keys: {', '.join(extra)}. Allowed: {', '.join(sorted(allowed))}",
            )
        )

    key = q.get("key")
    if not isinstance(key, str) or not key.strip():
        errors.append(BenchmarkError(f"{prefix}.key", "required non-empty string"))
    else:
        if key in seen_keys:
            errors.append(BenchmarkError(f"{prefix}.key", f"duplicate key {key!r}"))
        seen_keys.add(key)

    text = q.get("text")
    if not isinstance(text, str) or not text.strip():
        errors.append(BenchmarkError(f"{prefix}.text", "required non-empty string"))

    options = q.get("options")
    if not isinstance(options, list) or len(options) < 2:
        errors.append(
            BenchmarkError(f"{prefix}.options", "must be a list of at least 2 strings")
        )
        options = None
    elif not all(isinstance(o, str) and o.strip() for o in options):
        errors.append(
            BenchmarkError(
                f"{prefix}.options", "every option must be a non-empty string"
            )
        )
        options = None
    else:
        if len(set(options)) != len(options):
            errors.append(BenchmarkError(f"{prefix}.options", "duplicate option label"))

    dist = q.get("human_distribution")
    if not isinstance(dist, dict) or not dist:
        errors.append(
            BenchmarkError(
                f"{prefix}.human_distribution",
                "must be a non-empty mapping of option -> probability",
            )
        )
        return

    bad_value = False
    total = 0.0
    for label, p in dist.items():
        if not isinstance(label, str):
            errors.append(
                BenchmarkError(
                    f"{prefix}.human_distribution",
                    f"non-string option key: {label!r}",
                )
            )
            bad_value = True
            continue
        if not isinstance(p, (int, float)) or isinstance(p, bool):
            errors.append(
                BenchmarkError(
                    f"{prefix}.human_distribution.{label}",
                    "must be a number",
                )
            )
            bad_value = True
            continue
        if p < 0 or p > 1:
            errors.append(
                BenchmarkError(
                    f"{prefix}.human_distribution.{label}",
                    f"must be in [0, 1]; got {p}",
                )
            )
            bad_value = True
            continue
        total += float(p)

    if not bad_value and abs(total - 1.0) > _DIST_TOLERANCE:
        errors.append(
            BenchmarkError(
                f"{prefix}.human_distribution",
                f"must sum to 1.0 within {_DIST_TOLERANCE} (got {total:.4f})",
            )
        )

    if options is not None and not bad_value:
        missing = sorted(set(options) - set(dist))
        if missing:
            errors.append(
                BenchmarkError(
                    f"{prefix}.human_distribution",
                    f"missing mass for option(s): {', '.join(missing)}",
                )
            )
        unknown = sorted(set(dist) - set(options))
        if unknown:
            errors.append(
                BenchmarkError(
                    f"{prefix}.human_distribution",
                    f"option(s) not declared in options: {', '.join(unknown)}",
                )
            )

    topic = q.get("topic")
    if topic is not None and (not isinstance(topic, str) or not topic.strip()):
        errors.append(
            BenchmarkError(f"{prefix}.topic", "must be a non-empty string if set")
        )


def _check_questions(data: dict, errors: list[BenchmarkError]) -> None:
    qs = data.get("questions")
    if qs is None:
        errors.append(BenchmarkError("questions", "required"))
        return
    if not isinstance(qs, list):
        errors.append(BenchmarkError("questions", "must be a list"))
        return
    if len(qs) < _MIN_QUESTIONS:
        errors.append(
            BenchmarkError(
                "questions",
                f"a benchmark needs at least {_MIN_QUESTIONS} questions to be "
                f"worth scoring (got {len(qs)})",
            )
        )
    seen: set[str] = set()
    for i, q in enumerate(qs):
        _check_question(q, i, seen, errors)


def validate_benchmark(
    data: dict[str, Any],
) -> Union[UserBenchmark, list[BenchmarkError]]:
    """Validate a parsed benchmark dict against the schema.

    Returns a :class:`UserBenchmark` on success, or a list of
    :class:`BenchmarkError` on failure. All errors are collected in one
    pass so a contributor can fix everything before re-running.
    """
    errors: list[BenchmarkError] = []

    if not isinstance(data, dict):
        return [BenchmarkError("", "top-level benchmark must be a mapping")]

    unknown = sorted(set(data) - set(_ALLOWED_KEYS))
    if unknown:
        errors.append(
            BenchmarkError(
                "",
                f"unknown top-level keys: {', '.join(unknown)}. "
                f"Allowed: {', '.join(_ALLOWED_KEYS)}",
            )
        )

    benchmark_id = _check_str(data, "benchmark_id", errors)
    title = _check_str(data, "title", errors)
    contributor = _check_str(data, "contributor", errors)
    description = _check_str(data, "description", errors)
    domain = _check_str(data, "domain", errors)
    harness_version = _check_str(data, "harness_version", errors)

    _check_slug(benchmark_id, "benchmark_id", errors)
    _check_slug(domain, "domain", errors)
    _check_contributor(contributor, errors)
    _check_source(data, errors)
    _check_redistribution(data, errors)
    _check_questions(data, errors)

    notes = data.get("notes")
    if notes is not None and not isinstance(notes, str):
        errors.append(BenchmarkError("notes", "must be a string"))

    if errors:
        return errors

    assert benchmark_id and title and contributor and description
    assert domain and harness_version
    policy = data["redistribution_policy"]
    qs = data["questions"]
    canon = _canonicalise(data)
    return UserBenchmark(
        benchmark_id=benchmark_id,
        title=title,
        contributor=contributor,
        domain=domain,
        harness_version=harness_version,
        redistribution_policy=policy,
        n_questions=len(qs),
        raw=canon,
    )


def _canonicalise(data: dict[str, Any]) -> dict[str, Any]:
    """Reorder keys to match :data:`_ALLOWED_KEYS` so the embedded benchmark
    block is byte-stable across machines. Nested mappings (``source``, each
    question dict) keep their insertion order — only the top-level layout is
    normalised, the question hash handled separately by
    :func:`compute_benchmark_hash`.
    """
    return {k: data[k] for k in _ALLOWED_KEYS if k in data}


# --- Loading + validation (convenience) --------------------------------------


def load_and_validate(
    path: Union[str, Path],
) -> Union[UserBenchmark, list[BenchmarkError]]:
    """One-shot: read JSON from disk and validate. Returns either the parsed
    :class:`UserBenchmark` or a list of :class:`BenchmarkError`."""
    parsed = load_benchmark_file(path)
    if isinstance(parsed, BenchmarkError):
        return [parsed]
    return validate_benchmark(parsed)


# --- Hashing -----------------------------------------------------------------


def compute_benchmark_hash(benchmark: UserBenchmark) -> str:
    """Stable SHA-256 over the canonical questions block.

    The hash is keyed on the *questions* only (not the prose metadata like
    ``title`` or ``notes``) so a contributor can fix a typo in the
    description without minting a new benchmark identity downstream. Two
    submissions with the same ``benchmark_id`` but different question sets
    are treated as a collision by the server.

    We sort keys at every level and use compact separators so the same
    questions produce the same hash regardless of authoring order.
    """
    payload = json.dumps(
        benchmark.raw["questions"], sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --- Attaching to a submission body ------------------------------------------


def attach_to_submission_body(body: str, benchmark: UserBenchmark) -> str:
    """Return a new submission body string with ``user_benchmark`` stamped on.

    The input ``body`` MUST be valid JSON serialising a top-level object.
    We re-serialise compactly (no spaces, no trailing whitespace) so the
    server-side hash that anchors the leaderboard slice identity stays
    deterministic across CLI invocations.

    The stamped block carries a ``benchmark_hash`` computed from the
    canonicalised questions list — this is the field the server-side
    fanout (run-against-all-configs) keys on so a re-submission with the
    same content collapses to one slice instead of N.
    """
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError("submission body must be a JSON object at the top level")
    stamped = dict(benchmark.raw)
    stamped["benchmark_hash"] = compute_benchmark_hash(benchmark)
    data["user_benchmark"] = stamped
    return json.dumps(data, sort_keys=False, separators=(",", ":"))


def check_harness_version(benchmark: UserBenchmark) -> Optional[BenchmarkError]:
    """Compare ``benchmark.harness_version`` against the installed harness.

    Returns ``None`` on a match and a :class:`BenchmarkError` otherwise.
    Kept as a standalone helper so the CLI can downgrade the mismatch to a
    warning under ``--allow-harness-mismatch`` — mirrors the contract on
    :mod:`synthbench.user_config` exactly so contributors only learn one
    flag.
    """
    if benchmark.harness_version != __version__:
        return BenchmarkError(
            "harness_version",
            f"benchmark pins harness {benchmark.harness_version!r} but installed "
            f"synthbench is {__version__!r}. Re-score the dataset against the "
            f"pinned harness or bump the field deliberately.",
        )
    return None
