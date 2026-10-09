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

Parser versions (``config.option_parser_version``; absent key = v1):

* **v1** — the matching order above, verbatim. Kept callable so historical
  runs re-parse bit-for-bit.
* **v2** (current, synthbench#352) — newer models answer in markdown prose
  (``**(D) Depends on the situation.**`` followed by an explanation). v1
  counted those as parse failures, and its whole-text containment could
  mis-score them by matching an option mentioned in the explanation. v2:

  - strips markdown emphasis/heading/quote markup before matching;
  - accepts a *leading* option label (``(D) ...``, ``D. ...``, ``D) ...``)
    as the answer, unless the text right after it exactly names a
    different option (contradictory → parse failure);
  - restricts containment to the first line, falling back to the whole
    response only when exactly one option is contained in it.

  Refusal detection is unchanged (it is versioned separately).
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

#: Parser version stamped into run metadata (``config.option_parser_version``).
#: Absent key on a committed run file means v1.
OPTION_PARSER_VERSION = 2

# v2: markdown markup to drop before matching — emphasis runs (``**``,
# ``__``, ``*``), and line-leading heading / blockquote / bullet markers.
_MD_EMPHASIS_RE = re.compile(r"(\*{1,3}|_{2,3})")
_MD_LINE_PREFIX_RE = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]+|>[ \t]*|[-+][ \t]+)", re.MULTILINE
)

# v2: leading option label, optionally after an "Answer:" style prefix.
# Parenthesized letters may be either case; bare letters must be uppercase
# and delimited (checked in _leading_label_match) so "I think..." or
# "A lot of people..." never parse as a label.
_LEADING_LABEL_RE = re.compile(
    r"^\s*(?:(?:answer|my answer|choice)\s*[:\-]\s*)?"
    r"(?:\(([A-Za-z])\)|([A-Za-z])[.):](?=\s|$))\s*(.*)",
    re.IGNORECASE | re.DOTALL,
)
_PAREN_LABEL_RE = re.compile(r"\(([A-Za-z])\)")


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


def _strip_markdown(text: str) -> str:
    """Drop markdown emphasis and line-leading markup (v2)."""
    return _MD_EMPHASIS_RE.sub("", _MD_LINE_PREFIX_RE.sub("", text))


def _leading_label_match(text: str, options: list[str]) -> ParsedResponse | None:
    """Resolve a leading ``(D) ...`` / ``D. ...`` label (v2).

    Returns ``None`` when there is no label; a parse failure when the label
    is out of range or contradicted by an exact option name right after it.
    The lowercase bare form (``a. ...``) is not a label — only ``(a)``.
    """
    match = _LEADING_LABEL_RE.match(text)
    if not match:
        return None
    paren, bare, rest = match.groups()
    if bare is not None and not bare.isupper():
        return None
    letter = (paren or bare).upper()
    idx = ord(letter) - ord("A")
    if not 0 <= idx < len(options):
        return ParsedResponse()
    # "(B) Favor" where B is "Oppose": the label and the echoed text
    # disagree, so neither can be trusted.
    first_line = rest.strip().split("\n", 1)[0]
    by_norm = {_normalize(opt): opt for opt in options}
    echoed = by_norm.get(_normalize(first_line))
    if echoed is not None and echoed != options[idx]:
        return ParsedResponse()
    return ParsedResponse(option=options[idx])


def _parse_v2_options(stripped: str, options: list[str]) -> ParsedResponse:
    """v2 option matching on markdown-stripped text (after refusal checks)."""
    text = _strip_markdown(stripped).strip()
    if not text:
        return ParsedResponse()

    by_norm = {_normalize(opt): opt for opt in options}
    text_norm = _normalize(text)
    if text_norm in by_norm:
        return ParsedResponse(option=by_norm[text_norm])

    match = _BARE_LETTER_RE.match(text)
    if match:
        idx = ord(match.group(1).upper()) - ord("A")
        if 0 <= idx < len(options):
            return ParsedResponse(option=options[idx])
        return ParsedResponse()

    labelled = _leading_label_match(text, options)
    if labelled is not None:
        return labelled

    lines = [ln for ln in text.splitlines() if ln.strip()]
    # A parenthesized label after a short lead-in ("I'd say (B) agree",
    # possibly below a roleplay line like "*thinks*"). Only when the opening
    # lines carry exactly one distinct label; several means a list or a
    # comparison, not an answer.
    lead = "\n".join(lines[:2])
    labels = list(_PAREN_LABEL_RE.finditer(lead))
    if labels and len({m.group(1).upper() for m in labels}) == 1:
        inline = _leading_label_match(lead[labels[0].start() :], options)
        if inline is not None:
            return inline

    first_line = lines[0] if lines else ""
    contained = _containment_match(first_line, options)
    if contained is not None:
        return ParsedResponse(option=contained)

    # Whole-response containment only when unambiguous: an explanation that
    # mentions several options must not be scored as whichever matched first.
    hits = [opt for opt in options if _containment_match(text, [opt]) is not None]
    if len(hits) == 1:
        return ParsedResponse(option=hits[0])
    return ParsedResponse()


def parse_option_response(
    text: str,
    options: list[str],
    *,
    refusal_detector_version: int = REFUSAL_DETECTOR_VERSION,
    option_parser_version: int = OPTION_PARSER_VERSION,
) -> ParsedResponse:
    """Parse a raw model response into an option selection, refusal, or failure.

    Never falls back to ``options[0]``. See module docstring for the
    matching order and rationale.

    ``refusal_detector_version`` selects the refusal heuristic: 2 (default,
    answer-initial anchoring + option-echo exemption) or 1 (the legacy
    un-anchored patterns, kept callable so historical runs can be
    reproduced bit-for-bit).

    ``option_parser_version`` selects option matching the same way: 2
    (default, markdown-aware) or 1 (legacy).
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

    if option_parser_version >= 2:
        return _parse_v2_options(stripped, options)

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
