"""Refusal calibration metric (P_refuse) and refusal-text detection.

Two detector versions coexist:

* :func:`detect_refusal` — **v1** (retained verbatim for reproducibility of
  pre-v2 runs). Un-anchored substring patterns; known precision failure:
  chatty in-character answers ("I don't get sick much, I'd say good") match
  ``\\bI don't\\b`` anywhere in the text and are mis-flagged as refusals.
* :func:`detect_refusal_v2` — **v2** (current default via
  :data:`REFUSAL_DETECTOR_VERSION`). Patterns must be answer-INITIAL
  (anchored to the start of the trimmed response, tolerating leading
  pleasantries like "Well," / "Hmm,"), and never fire when the response
  contains a valid option for the current question (option-echo exemption —
  required because some instruments carry substantive options containing
  refusal-ish text, e.g. GSS GOD's "don't know, no way to find out").

Runs are stamped with ``config.refusal_detector_version``; the key is
additive — files without it were parsed under v1. The stamp is metadata
only and never feeds :func:`synthbench.config_id.build_config_id`, so
every historical config_id is unchanged.
"""

from __future__ import annotations

import re

#: Detector version stamped into run metadata (``config.refusal_detector_version``).
#: Absent key on a committed run file means v1.
REFUSAL_DETECTOR_VERSION = 2

# Patterns that indicate an LLM-style refusal when explicit refusal field is
# unavailable. v1 — un-anchored; kept callable for reproducibility.
_REFUSAL_PATTERNS = [
    re.compile(r"\bI cannot\b", re.IGNORECASE),
    re.compile(r"\bI can't\b", re.IGNORECASE),
    re.compile(r"\bI don't\b", re.IGNORECASE),
    re.compile(r"\bAs an AI\b", re.IGNORECASE),
    re.compile(r"\bI'm not able to\b", re.IGNORECASE),
    re.compile(r"\bI am not able to\b", re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# v2 detector
# ---------------------------------------------------------------------------

# Leading pleasantries / hedges an in-character respondent may open with
# before the substantive part of the answer. Stripped (repeatedly) before
# the answer-initial anchor check, so "Well, I can't answer that" is still
# a refusal while "Well, I don't get sick much" is judged on its own text.
_PLEASANTRY_PREFIX_RE = re.compile(
    r"^(?:(?:well|hmm+|hm+|oh(?:\s+man|\s+boy)?|um+|uh+|ah+|honestly|okay|ok|"
    r"you know|look|gosh|geez|man|wow|huh|ha|haha|heh|so|hey|yeah|sure|right)"
    r"[\s,.!…:;—-]+)+",
    re.IGNORECASE,
)

# Wrapping quote/formatting characters models sometimes emit around answers.
_WRAPPING_CHARS = "\"'`*_“”‘’ \t\r\n"

# Answer-initial refusal patterns. All are anchored with ``\A`` and applied
# AFTER the pleasantry prefix is stripped. The v1 ``\bI don't\b`` footgun is
# narrowed to explicit nonresponse continuations so first-person substantive
# answers ("I don't get sick much...") never match.
_REFUSAL_PATTERNS_V2 = [
    re.compile(r"\AI cannot\b", re.IGNORECASE),
    re.compile(r"\AI can't\b", re.IGNORECASE),
    re.compile(r"\AI won't\b", re.IGNORECASE),
    re.compile(r"\AI refuse\b", re.IGNORECASE),
    re.compile(r"\AI decline\b", re.IGNORECASE),
    re.compile(r"\AI(?:'d| would)? ?(?:prefer|rather) not\b", re.IGNORECASE),
    re.compile(r"\AI'?m not able to\b", re.IGNORECASE),
    re.compile(r"\AI am not able to\b", re.IGNORECASE),
    re.compile(r"\AI'?m not comfortable\b", re.IGNORECASE),
    re.compile(r"\AAs an AI\b", re.IGNORECASE),
    re.compile(r"\AAs a(?:n)? (?:language |large language )?model\b", re.IGNORECASE),
    re.compile(r"\AI'?m (?:just )?an AI\b", re.IGNORECASE),
    re.compile(
        r"\AI don'?t (?:know|have (?:an |a )?(?:opinion|answer|preference|view)|"
        r"feel comfortable|want to (?:answer|say)|wish to answer)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\ANo comment\b", re.IGNORECASE),
    re.compile(r"\A(?:Sorry|I'?m sorry|I apologi[sz]e)\b[,.]?\s", re.IGNORECASE),
]

_V2_WS_RE = re.compile(r"\s+")


def _v2_normalize(text: str) -> str:
    """Case-fold, collapse whitespace, strip wrapping punctuation."""
    text = _V2_WS_RE.sub(" ", str(text)).strip().lower()
    return text.strip("\"'`.,;:!()[]{} ")


# Minimum normalized length for an option to participate in the echo
# exemption. Very short options ("No", "Yes") occur as ordinary words inside
# genuine refusals ("As an AI, I have no view here") — treating those as
# echoes would reintroduce the v1-era "no-inside-refusal" false votes.
_MIN_ECHO_OPTION_LEN = 4


def _mentions_option(text: str, options: list[str]) -> bool:
    """True if *text* plausibly echoes one of the declared options.

    Two forms count as an echo:

    * a declared option (normalized length >= 4) appears in the response
      with word boundaries on both sides ("I'd say Good" echoes option
      "good"); or
    * the (normalized) response is itself a substring of a declared option
      — a partial echo of a long option ("don't know" against GSS GOD's
      substantive "don't know, no way to find out" option), which must not
      be classified as a refusal when the instrument offers it as an
      answer.
    """
    text_norm = _v2_normalize(text)
    if not text_norm:
        return False
    for opt in options:
        opt_norm = _v2_normalize(opt)
        if len(opt_norm) < _MIN_ECHO_OPTION_LEN:
            continue
        pattern = r"(?<!\w)" + re.escape(opt_norm) + r"(?!\w)"
        if re.search(pattern, text_norm):
            return True
        if len(text_norm) >= _MIN_ECHO_OPTION_LEN and text_norm in opt_norm:
            return True
    return False


def detect_refusal_v2(text: str, options: list[str] | None = None) -> bool:
    """Detect refusal — v2: answer-initial anchoring + option-echo exemption.

    A response is a refusal only when a refusal pattern matches at the
    START of the trimmed response (after skipping leading pleasantries such
    as "Well," / "Hmm,"), AND the response does not contain a valid option
    for the current question. The exemption exists because in-character
    answers routinely open with refusal-shaped text before naming an option
    ("I don't get sick much, I'd say good" — a vote for "good", not a
    refusal), and some instruments include substantive options that
    themselves contain refusal-ish phrases.

    Args:
        text: Raw response text from the provider.
        options: Declared answer options for the current question. When
            provided, an option echo suppresses refusal classification.

    Returns:
        True if the text is an answer-initial refusal with no option echo.
    """
    stripped = str(text).strip(_WRAPPING_CHARS)
    if not stripped:
        return False
    stripped = _PLEASANTRY_PREFIX_RE.sub("", stripped)
    if not any(p.search(stripped) for p in _REFUSAL_PATTERNS_V2):
        return False
    if options and _mentions_option(str(text), options):
        return False
    return True


def refusal_calibration(
    provider_refusal_rates: list[float],
    human_refusal_rates: list[float],
) -> float:
    """Compute refusal calibration: P_refuse = 1 - mean(|R_provider - R_human|).

    Measures whether the provider's refusal rate matches human refusal patterns.
    A provider that never refuses when humans sometimes do (or vice versa) gets
    a lower score.

    Args:
        provider_refusal_rates: Per-question refusal rates from the provider.
            Each value in [0, 1].
        human_refusal_rates: Per-question refusal rates from human data.
            Each value in [0, 1].

    Returns:
        P_refuse in [0, 1]. Higher = better calibrated refusals.
        Returns 1.0 if no questions provided.
    """
    if not provider_refusal_rates or not human_refusal_rates:
        return 1.0

    n = min(len(provider_refusal_rates), len(human_refusal_rates))
    total_diff = sum(
        abs(provider_refusal_rates[i] - human_refusal_rates[i]) for i in range(n)
    )
    mean_diff = total_diff / n

    return max(0.0, min(1.0, 1.0 - mean_diff))


def detect_refusal(text: str) -> bool:
    """Detect refusal from response text using common LLM refusal patterns.

    For providers without an explicit refusal field, this heuristic checks
    the raw response text for common refusal phrases.

    Args:
        text: Raw response text from the provider.

    Returns:
        True if the text appears to be a refusal.
    """
    return any(p.search(text) for p in _REFUSAL_PATTERNS)


def extract_human_refusal_rate(human_distribution: dict[str, float]) -> float:
    """Extract refusal rate from a human response distribution.

    Looks for option keys that indicate refusal (e.g., "Refused",
    "Don't know/Refused"). Returns the combined probability mass of
    refusal-like options.

    Args:
        human_distribution: Human response distribution for a question.

    Returns:
        Refusal rate in [0, 1].
    """
    refusal_keys = [
        k
        for k in human_distribution
        if isinstance(k, str)
        and (
            re.search(r"\brefused?\b", k, re.IGNORECASE)
            or re.search(r"\bdon'?t know\b", k, re.IGNORECASE)
        )
    ]
    return sum(human_distribution.get(k, 0.0) for k in refusal_keys)


def refusal_rate(dist: dict[str, float]) -> float:
    """Extract the explicit "Refused" option probability from a distribution.

    OpinionsQA includes "Refused" as an explicit answer option in 677 of 684
    questions. This function reads that option directly — no text parsing.

    Args:
        dist: Response distribution mapping option text to probability.

    Returns:
        Probability mass on the "Refused" option, or 0.0 if absent.
    """
    return dist.get("Refused", 0.0)


def p_refuse(
    model_dist: dict[str, float],
    human_dist: dict[str, float],
) -> float | None:
    """Per-question refusal calibration via the explicit "Refused" option.

    P_refuse_q = 1.0 - |refusal_rate(model) - refusal_rate(human)|

    For questions where neither distribution contains a "Refused" option,
    returns None (exclude from aggregate).

    Args:
        model_dist: Model response distribution for one question.
        human_dist: Human response distribution for one question.

    Returns:
        P_refuse in [0, 1], or None if the question has no "Refused" option.
    """
    has_refused = "Refused" in model_dist or "Refused" in human_dist
    if not has_refused:
        return None
    return 1.0 - abs(refusal_rate(model_dist) - refusal_rate(human_dist))
