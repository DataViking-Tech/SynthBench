"""Shared option-response parsing for all providers.

Historically every provider carried its own private ``_parse_letter`` copy
with two systematic bugs:

1. The letter match was un-anchored (``^\\(?([A-Z])\\)?``), so a model that
   echoed option *text* was parsed by its first character: options
   ``["Better", "Worse"]`` + response ``"Better"`` parsed as **"Worse"**
   (``B`` -> index 1).
2. The fallback was a raw substring test, so ``"Disagree"`` matched
   ``"Agree"`` first, and refusal text like ``"I cannot answer"`` matched
   ``"No"`` (``"no" in "cannot"``).

Parse failures were then silently coerced to ``options[0]``, biasing every
published distribution toward the first option.

This module is the single replacement. Matching order:

1. Exact (normalized) full-string equality against the option text — an
   unambiguous echo of an option always wins.
2. Refusal detection (:func:`synthbench.metrics.refusal.detect_refusal`)
   runs BEFORE any fuzzy option matching, so refusal text can never be
   substring-matched into a vote.
3. Bare option letter, anchored as a full match (``"B"``, ``"(c)"``,
   ``"A."`` — but never the leading character of a longer word).
4. Word-boundary containment against the option text, longest option
   first, as a last resort (``"I'd say Disagree"`` -> ``"Disagree"``).

Anything else is a parse failure: ``option is None`` and ``refusal`` is
False. Callers must NOT substitute a default option.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from synthbench.metrics.refusal import (
    REFUSAL_DETECTOR_VERSION,
    detect_refusal,
    detect_refusal_v2,
)

# Full-match bare letter: optional "(", one ASCII letter, optional ")",
# optional trailing ".", ")" or ":", nothing else but whitespace.
_BARE_LETTER_RE = re.compile(r"^\s*\(?([A-Za-z])\)?[.):]?\s*$")

_WS_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class ParsedResponse:
    """Outcome of parsing one raw model response.

    Exactly one of three states:

    * option selected: ``option`` is the matched option text, ``refusal``
      is False.
    * refusal: ``option`` is None, ``refusal`` is True.
    * parse failure: ``option`` is None, ``refusal`` is False.
    """

    option: str | None = None
    refusal: bool = False

    @property
    def is_parse_failure(self) -> bool:
        return self.option is None and not self.refusal


def _normalize(text: str) -> str:
    """Case-fold, collapse whitespace, and strip surrounding punctuation."""
    text = _WS_RE.sub(" ", str(text)).strip().lower()
    # Strip wrapping punctuation/quotes but keep interior punctuation so
    # options like "Don't know" still compare correctly.
    return text.strip("\"'`.,;:!()[]{} ")


def _containment_match(text: str, options: list[str]) -> str | None:
    """Word-boundary containment, longest option first.

    Longest-first ordering prevents "Agree" from shadowing "Disagree"-style
    superstring options; the word boundary (non-word characters on both
    sides) prevents "no" from matching inside "cannot".
    """
    text_norm = _normalize(text)
    if not text_norm:
        return None
    for opt in sorted(options, key=lambda o: len(_normalize(o)), reverse=True):
        opt_norm = _normalize(opt)
        if not opt_norm:
            continue
        pattern = r"(?<!\w)" + re.escape(opt_norm) + r"(?!\w)"
        if re.search(pattern, text_norm):
            return opt
    return None


def parse_option_response(
    text: str,
    options: list[str],
    *,
    refusal_detector_version: int = REFUSAL_DETECTOR_VERSION,
) -> ParsedResponse:
    """Parse a raw model response into an option selection, refusal, or failure.

    Never falls back to ``options[0]``. See module docstring for the
    matching order and rationale.

    ``refusal_detector_version`` selects the refusal heuristic: 2 (default,
    answer-initial anchoring + option-echo exemption) or 1 (the legacy
    un-anchored patterns, kept callable so historical runs can be
    reproduced bit-for-bit).
    """
    raw = str(text)
    stripped = raw.strip()
    if not stripped:
        return ParsedResponse()

    # 1. Exact normalized equality — an unambiguous echo of an option wins
    # even over refusal-pattern heuristics (an option worded in the first
    # person, e.g. "I don't know", is a legitimate selection when echoed
    # verbatim).
    text_norm = _normalize(stripped)
    by_norm = {_normalize(opt): opt for opt in options}
    if text_norm in by_norm:
        return ParsedResponse(option=by_norm[text_norm])

    # 2. Refusal detection BEFORE fuzzy option matching.
    if refusal_detector_version >= 2:
        is_refusal = detect_refusal_v2(stripped, options)
    else:
        is_refusal = detect_refusal(stripped)
    if is_refusal:
        return ParsedResponse(refusal=True)

    # 3. Bare letter, anchored full-match only.
    match = _BARE_LETTER_RE.match(stripped)
    if match:
        idx = ord(match.group(1).upper()) - ord("A")
        if 0 <= idx < len(options):
            return ParsedResponse(option=options[idx])
        return ParsedResponse()

    # 4. Word-boundary containment, longest option first.
    contained = _containment_match(stripped, options)
    if contained is not None:
        return ParsedResponse(option=contained)

    return ParsedResponse()
