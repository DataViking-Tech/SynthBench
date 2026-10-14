"""Routing topic taxonomy (version 1) and per-question topic lookup.

Seven topics, shared with Althing through ``routing.json`` (see
``docs/routing-json-api.md``). Every question gets its topic from a
committed, key-based label file under ``synthbench/data/topics/`` when one
exists:

* OpinionsQA labels come from the dataset's official coarse topic mapping
  (``topic_mapping.npy``, first ``cg`` entry), mapped through
  :data:`OPINIONSQA_COARSE_TO_TOPIC`.
* SubPOP, GSS and GlobalOpinionQA labels come from a model labeler
  (``scripts/label-topics.py``) validated against the OpinionsQA labels.

Keys without a committed label fall back to :func:`keyword_topic`, a
keyword classifier over the same seven topics. Keywords match on word
boundaries only, never as substrings ("nation" does not match
"discrimination").
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

TAXONOMY_VERSION = 1


@dataclass(frozen=True)
class Topic:
    id: str
    label: str
    description: str
    keywords: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "keywords": list(self.keywords),
        }


TOPICS: tuple[Topic, ...] = (
    Topic(
        id="politics",
        label="Politics and policy",
        description=(
            "Elections, parties, government, political leaders, laws and "
            "public policy, immigration."
        ),
        keywords=(
            "abortion",
            "ballot",
            "biden",
            "campaign",
            "congress",
            "conservative",
            "conservatives",
            "court",
            "courts",
            "death penalty",
            "democrat",
            "democrats",
            "democratic party",
            "deportation",
            "elected",
            "election",
            "elections",
            "government",
            "governor",
            "gun",
            "guns",
            "immigrant",
            "immigrants",
            "immigration",
            "law",
            "laws",
            "legal",
            "legislation",
            "liberal",
            "liberals",
            "mayor",
            "obama",
            "officials",
            "parliament",
            "partisan",
            "political",
            "politician",
            "politicians",
            "politics",
            "president",
            "presidential",
            "prime minister",
            "republican",
            "republicans",
            "senate",
            "supreme court",
            "trump",
            "vote",
            "voters",
            "votes",
            "voting",
        ),
    ),
    Topic(
        id="economy",
        label="Economy and work",
        description=(
            "The economy, jobs and careers, income and inequality, personal "
            "finances, social class."
        ),
        keywords=(
            "afford",
            "business",
            "businesses",
            "career",
            "cost of living",
            "debt",
            "economic",
            "economy",
            "employer",
            "employment",
            "finances",
            "financial",
            "financially",
            "income",
            "inequality",
            "inflation",
            "job",
            "jobs",
            "labor",
            "middle class",
            "money",
            "poverty",
            "prices",
            "recession",
            "retirement",
            "rich",
            "salary",
            "savings",
            "social class",
            "social security",
            "tax",
            "taxes",
            "trade",
            "unemployment",
            "union",
            "unions",
            "wage",
            "wages",
            "wealth",
            "wealthy",
            "work",
            "workers",
        ),
    ),
    Topic(
        id="technology",
        label="Technology and media",
        description=(
            "Technology and automation, the internet and social media, news "
            "media, data and privacy, large companies and banks."
        ),
        keywords=(
            "algorithm",
            "algorithms",
            "artificial intelligence",
            "automation",
            "banks",
            "companies",
            "computer",
            "computers",
            "corporations",
            "cybersecurity",
            "data",
            "digital",
            "facebook",
            "fake news",
            "internet",
            "journalist",
            "journalists",
            "media",
            "misinformation",
            "news",
            "newspaper",
            "newspapers",
            "online",
            "personal information",
            "privacy",
            "robot",
            "robots",
            "smartphone",
            "social media",
            "software",
            "tech",
            "technology",
            "technologies",
            "television",
            "twitter",
            "website",
            "websites",
        ),
    ),
    Topic(
        id="science-health",
        label="Science and health",
        description=(
            "Science and scientists, the environment and climate, medicine, "
            "the health care system, personal health, and the condition of "
            "local communities (local problems, neighbors, urban and rural life)."
        ),
        keywords=(
            "climate",
            "climate change",
            "coronavirus",
            "covid",
            "disease",
            "doctor",
            "doctors",
            "drug",
            "drugs",
            "energy",
            "environment",
            "environmental",
            "exercise",
            "global warming",
            "health",
            "health care",
            "health insurance",
            "healthcare",
            "hospital",
            "hospitals",
            "illness",
            "medical",
            "medicine",
            "mental health",
            "pandemic",
            "pollution",
            "research",
            "science",
            "scientific",
            "scientists",
            "space",
            "vaccine",
            "vaccines",
        ),
    ),
    Topic(
        id="identity",
        label="Identity and values",
        description=(
            "Race and ethnicity, gender and sexuality, discrimination, "
            "religion, personal values and morality."
        ),
        keywords=(
            "bible",
            "black",
            "catholic",
            "christian",
            "christians",
            "church",
            "churches",
            "discrimination",
            "diversity",
            "ethnic",
            "evangelical",
            "faith",
            "feminism",
            "feminist",
            "gay",
            "gender",
            "god",
            "hispanic",
            "homosexual",
            "islam",
            "jewish",
            "latino",
            "lesbian",
            "men",
            "moral",
            "morally",
            "muslim",
            "muslims",
            "prayer",
            "prejudice",
            "race",
            "racial",
            "racism",
            "religion",
            "religious",
            "same-sex",
            "sexual",
            "sexuality",
            "transgender",
            "values",
            "white",
            "women",
        ),
    ),
    Topic(
        id="society",
        label="Family, community and safety",
        description=(
            "Family and relationships, crime and safety, education, and how "
            "people see the future."
        ),
        keywords=(
            "child",
            "children",
            "college",
            "community",
            "crime",
            "criminal",
            "criminals",
            "divorce",
            "education",
            "families",
            "family",
            "friends",
            "future",
            "happy",
            "kids",
            "life",
            "marriage",
            "married",
            "neighborhood",
            "neighbors",
            "parent",
            "parents",
            "police",
            "relationship",
            "relationships",
            "safe",
            "safety",
            "school",
            "schools",
            "students",
            "teachers",
            "trust",
            "university",
            "violence",
        ),
    ),
    Topic(
        id="global",
        label="Global affairs",
        description=(
            "Foreign policy, other countries and international relations, "
            "war and security, global institutions."
        ),
        keywords=(
            "allies",
            "ally",
            "china",
            "chinese",
            "countries",
            "diplomacy",
            "europe",
            "european union",
            "foreign",
            "foreign policy",
            "germany",
            "india",
            "international",
            "iran",
            "israel",
            "japan",
            "military",
            "nato",
            "nuclear",
            "refugees",
            "russia",
            "sanctions",
            "terrorism",
            "terrorist",
            "troops",
            "ukraine",
            "united nations",
            "war",
            "wars",
            "world",
        ),
    ),
)

TOPIC_IDS: tuple[str, ...] = tuple(t.id for t in TOPICS)
TOPIC_LABELS: dict[str, str] = {t.id: t.label for t in TOPICS}
TOPICS_BY_ID: dict[str, Topic] = {t.id: t for t in TOPICS}

# OpinionsQA coarse topics (topic_mapping.npy ``cg``) -> taxonomy id.
OPINIONSQA_COARSE_TO_TOPIC: dict[str, str] = {
    "political issues": "politics",
    "leadership": "politics",
    "immigration": "politics",
    "economy and inequality": "economy",
    "personal finance": "economy",
    "job/career": "economy",
    "status in life": "economy",
    "news, social media, data, privacy": "technology",
    "corporations, banks, technology and automation": "technology",
    "science": "science-health",
    "community health": "science-health",
    "healthcare system": "science-health",
    "personal health": "science-health",
    "race": "identity",
    "gender & sexuality": "identity",
    "discrimination": "identity",
    "religion": "identity",
    "self-perception and values": "identity",
    "relationships and family": "society",
    "crime/security": "society",
    "education": "society",
    "future": "society",
    "global attitudes and foreign policy": "global",
}

LABELS_DIR = Path(__file__).parent / "data" / "topics"


def taxonomy_dict() -> dict:
    """The taxonomy block published in ``routing.json`` and ``leaderboard.json``."""
    return {"version": TAXONOMY_VERSION, "topics": [t.as_dict() for t in TOPICS]}


def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    # Word boundaries on both sides; inner spaces match any run of whitespace.
    body = r"\s+".join(re.escape(part) for part in keyword.split())
    return re.compile(rf"\b{body}\b")


_PATTERNS: tuple[tuple[str, tuple[re.Pattern[str], ...]], ...] = tuple(
    (t.id, tuple(_keyword_pattern(k) for k in t.keywords)) for t in TOPICS
)


def keyword_topic(text: str) -> str | None:
    """Classify ``text`` by keyword hits; ``None`` when nothing matches.

    Each topic scores the number of its keywords found in the lowercased
    text (word-boundary match). The highest score wins; ties go to the
    topic listed first in :data:`TOPICS`.
    """
    if not text:
        return None
    lowered = text.lower()
    best_id: str | None = None
    best_hits = 0
    for topic_id, patterns in _PATTERNS:
        hits = sum(1 for p in patterns if p.search(lowered))
        if hits > best_hits:
            best_id, best_hits = topic_id, hits
    return best_id


def _base_dataset(dataset: str | None) -> str:
    # Wave/year suffixes ("ntia (Nov 2023)") name the same dataset.
    return (dataset or "").split(" ", 1)[0].strip().lower()


@lru_cache(maxsize=None)
def load_labels(dataset: str) -> dict[str, str]:
    """Committed ``{question key: topic id}`` labels for ``dataset`` (may be empty)."""
    path = LABELS_DIR / f"{_base_dataset(dataset)}.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    labels = data.get("labels") or {}
    return {str(k): v for k, v in labels.items() if v in TOPICS_BY_ID}


def label_for(dataset: str | None, key: str | None) -> str | None:
    """The committed label for ``(dataset, key)``, or ``None``."""
    if not dataset or not key:
        return None
    return load_labels(_base_dataset(dataset)).get(key)


def topic_for(dataset: str | None, key: str | None, text: str | None) -> str | None:
    """Topic id for a question: committed label first, keyword fallback second."""
    return label_for(dataset, key) or keyword_topic(text or "")


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------

FALLBACK_CATEGORY: str = "Other"
CATEGORIES: list[str] = [t.label for t in TOPICS] + [FALLBACK_CATEGORY]


def categorize_question(text: str) -> str:
    """Topic *label* for ``text`` from the keyword classifier.

    Kept for callers that only have question text. Returns
    :data:`FALLBACK_CATEGORY` when no keyword matches. Prefer
    :func:`topic_for`, which also uses the committed key-based labels.
    """
    topic_id = keyword_topic(text)
    return TOPIC_LABELS[topic_id] if topic_id else FALLBACK_CATEGORY
