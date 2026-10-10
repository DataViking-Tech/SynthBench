"""Refusal calibration metric (P_refuse) and refusal-text detection.

Two detector versions coexist:

* :func:`detect_refusal` — **v1** (retained verbatim for reproducibility of
  pre-v2 runs). Un-anchored substring patterns; known precision failure:
  chatty in-character answers ("I don't get sick much, I'd say good") match
  ``\\bI don't\\b`` anywhere in the text and are mis-flagged as refusals.
* :func:`detect_refusal_v2` — **v2**. Patterns must be answer-INITIAL
  (anchored to the start of the trimmed response, tolerating leading
  pleasantries like "Well," / "Hmm,"), and never fire when the response
  contains a valid option for the current question (option-echo exemption —
  required because some instruments carry substantive options containing
  refusal-ish text, e.g. GSS GOD's "don't know, no way to find out").
* :func:`detect_refusal_v3` — **v3** (current default via
  :data:`REFUSAL_DETECTOR_VERSION`, synthbench#356). v2 missed common
  character breaks from newer models — "I don't have a *personal* opinion
  …", "I don't have a country …", "I don't think I should pick …", and
  non-initial declines such as "The premise is outdated … so I can't pick
  one of these options". Those fell through as parse failures instead of
  refusals. v3 adds answer-initial "no stake / no standing" openers and
  an explicit non-selection pattern searched anywhere in the first
  paragraph. v2's option-echo exemption applies only when exactly one
  option is echoed (a response weighing both sides chose neither), and
  v3 adds a single-label exemption: a response carrying exactly one
  option label (``(B)``) picked an answer, so it is never a refusal.
* :func:`detect_refusal_v4` — **v4** (current default). v3 anchored its
  character-break openers to the start of the response, so a decline
  behind a lead-in ("I appreciate the roleplay setup, but I should be
  straightforward: I can't authentically answer this ...", "I'm Claude,
  an AI, and I don't actually live anywhere") fell through as a parse
  failure. Parse failures are dropped from the distribution, so a model
  whose refusals took that shape paid no refusal penalty: Haiku 4.5 logged
  22% parse failures and 0.7% refusals on SubPOP, and nearly all of those
  failures were refusals. v4 also searches the first paragraph for
  explicit character breaks (identifying as an AI, stepping out of the
  role, declining to answer "authentically", disclaiming personal beliefs
  or a place to live). v3's single-option exemptions still come first.

Runs are stamped with ``config.refusal_detector_version``; the key is
additive — files without it were parsed under v1. The stamp is metadata
only and never feeds :func:`synthbench.config_id.build_config_id`, so
every historical config_id is unchanged.
"""

from __future__ import annotations

import re

#: Detector version stamped into run metadata (``config.refusal_detector_version``).
#: Absent key on a committed run file means v1.
REFUSAL_DETECTOR_VERSION = 4

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


# ---------------------------------------------------------------------------
# v3 detector
# ---------------------------------------------------------------------------

# Additional answer-initial openers: the respondent says it has no opinion,
# stake, or standing to answer ("I don't have a personal opinion of ...",
# "I don't have a country ..."), or that answering isn't its place.
_REFUSAL_PATTERNS_V3_INITIAL = [
    re.compile(
        r"\AI (?:do not|don'?t) have (?:a |an |any )?(?:personal |real |genuine |strong |own )?"
        r"(?:opinions?|views?|stake|preferences?|country|nationality|personal experience|"
        r"lived experience|political (?:views?|opinions?|affiliation))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\AI (?:do not|don'?t) think (?:I should|it'?s (?:my place|appropriate|right|fair) to|"
        r"it would be (?:appropriate|right|fair) (?:for me )?to) "
        r"(?:pick|choose|select|answer|take a side|weigh in|rate)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\AI'?m (?:just )?an? (?:AI|artificial intelligence|(?:large )?language model)\b",
        re.IGNORECASE,
    ),
]

# Explicit non-selection anywhere in the first paragraph ("..., so I can't
# pick one of these options", "I won't pick (A) or (B)"). Requires a
# selection verb, so "I can't believe ..." / "I won't lie, ..." never match.
_NON_SELECTION_RE = re.compile(
    r"\bI (?:can'?t|cannot|won'?t|will not|shouldn'?t|should not|am not going to|'?m not going to)\s+"
    r"(?:honestly |really |fairly |just )?(?:pick|choose|select|rate|give (?:a|an|my) (?:rating|answer))\b",
    re.IGNORECASE,
)

_OPTION_LABEL_RE = re.compile(r"\(([A-Za-z])\)")


def _first_paragraph(text: str) -> str:
    for block in re.split(r"\n\s*\n", text.strip()):
        if block.strip():
            return block
    return ""


def _single_option_label(text: str, options: list[str]) -> bool:
    """True when *text* names exactly one in-range option label like ``(B)``."""
    letters = {m.group(1).upper() for m in _OPTION_LABEL_RE.finditer(text)}
    return len(letters) == 1 and 0 <= ord(next(iter(letters))) - ord("A") < len(options)


def detect_refusal_v3(text: str, options: list[str] | None = None) -> bool:
    """Detect refusal — v3: v2 plus character-break openers and non-selection.

    Classification order:

    1. A response that echoes exactly one declared option (v2's exemption,
       narrowed: discussing *both* sides is not choosing one) or names
       exactly one option label (``(B)``) chose an answer: not a refusal.
    2. Any v2 answer-initial pattern, or a v3 answer-initial "no opinion /
       no stake / not my place" opener: refusal.
    3. An explicit non-selection ("I can't pick one of these options",
       "I won't pick (A) or (B)") anywhere in the first paragraph: refusal.

    Args:
        text: Raw response text from the provider.
        options: Declared answer options for the current question.

    Returns:
        True if the response declines to choose an option.
    """
    raw = str(text)
    stripped = raw.strip(_WRAPPING_CHARS)
    if not stripped:
        return False
    if options:
        echoed = sum(1 for opt in options if _mentions_option(raw, [opt]))
        if echoed == 1 or _single_option_label(raw, options):
            return False
    opening = _PLEASANTRY_PREFIX_RE.sub("", stripped)
    if any(p.search(opening) for p in _REFUSAL_PATTERNS_V2):
        return True
    if any(p.search(opening) for p in _REFUSAL_PATTERNS_V3_INITIAL):
        return True
    return bool(_NON_SELECTION_RE.search(_first_paragraph(stripped)))


# ---------------------------------------------------------------------------
# v4 detector
# ---------------------------------------------------------------------------

# Character breaks searched anywhere in the first paragraph. Each names the
# model as an AI or explicitly declines to answer as the respondent, so an
# in-character opinion ("I can't stand ...", "I don't have strong feelings")
# never matches.
_CHARACTER_BREAK_RE = re.compile(
    r"\bI(?:'m| am) (?:Claude\b|an AI\b|an artificial intelligence\b|an? (?:large )?language model\b)"
    r"|\bAs an AI\b"
    r"|\b(?:step|stepping|break|breaking) (?:out of (?:the |this |my )?(?:particular )?"
    r"(?:role-?play|role|character|persona)|character\b)"
    r"|\beven (?:in|as) (?:a |an |the |this |my )?(?:character|role-?play|persona|fictional)"
    r"|\bI (?:can'?t|cannot|won'?t|shouldn'?t) (?:authentically |genuinely |honestly |truthfully )?"
    r"pretend\b"
    r"|\bI(?: can'?t| cannot| won'?t| shouldn'?t|'?m not able to| am not able to) "
    r"(?:authentically|genuinely|honestly|truthfully) "
    r"(?:answer|respond|adopt|role-?play|represent|express|take|provide|give|pick|choose|speak)\b"
    r"|\bI (?:can'?t|cannot|won'?t|shouldn'?t) (?:provide|give|offer|take) (?:a|an|any|my) "
    r"(?:particular |specific |personal |political )?(?:answer|position|stance|side)\b"
    r"|\bI'?m not comfortable (?:selecting|choosing|picking|answering|role-?playing|taking|"
    r"expressing|giving|sharing|presenting)\b"
    r"|\bI (?:don'?t|do not) think it'?s appropriate for me to\b"
    r"|\bI (?:don'?t|do not) (?:actually |really |genuinely )?(?:hold|have) (?:any )?"
    r"(?:personal|genuine|real|authentic) (?:political )?"
    r"(?:beliefs?|opinions?|views?|convictions?|stances?|experiences?)\b"
    r"|\bI (?:don'?t|do not) actually live\b",
    re.IGNORECASE,
)

# Roleplay stage directions ("*pauses thoughtfully*") before the first real
# paragraph.
_STAGE_DIRECTION_RE = re.compile(r"\A(?:\s*\*[^*\n]{1,80}\*\s*)+")


def detect_refusal_v4(text: str, options: list[str] | None = None) -> bool:
    """Detect refusal — v4: v3 plus character breaks anywhere in paragraph one.

    Classification order:

    1. v3's exemptions: exactly one echoed option or one option label is an
       answer, never a refusal.
    2. Any v3 refusal (answer-initial patterns, explicit non-selection).
    3. An explicit character break anywhere in the first paragraph (see
       :data:`_CHARACTER_BREAK_RE`): refusal.

    Args:
        text: Raw response text from the provider.
        options: Declared answer options for the current question.

    Returns:
        True if the response declines to choose an option.
    """
    raw = str(text)
    stripped = raw.strip(_WRAPPING_CHARS)
    if not stripped:
        return False
    if options:
        echoed = sum(1 for opt in options if _mentions_option(raw, [opt]))
        if echoed == 1 or _single_option_label(raw, options):
            return False
    if detect_refusal_v3(raw, options):
        return True
    body = _STAGE_DIRECTION_RE.sub("", raw.strip())
    return bool(_CHARACTER_BREAK_RE.search(_first_paragraph(body)))


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
