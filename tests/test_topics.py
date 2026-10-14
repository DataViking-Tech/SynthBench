"""Tests for the routing topic taxonomy, committed labels and keyword fallback."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from synthbench.topics import (
    CATEGORIES,
    FALLBACK_CATEGORY,
    LABELS_DIR,
    OPINIONSQA_COARSE_TO_TOPIC,
    TAXONOMY_VERSION,
    TOPIC_IDS,
    TOPIC_LABELS,
    TOPICS,
    categorize_question,
    keyword_topic,
    label_for,
    load_labels,
    taxonomy_dict,
    topic_for,
)

REPO = Path(__file__).resolve().parent.parent
LABELED_DATASETS = ("opinionsqa", "subpop", "gss", "globalopinionqa")


class TestTaxonomy:
    def test_seven_topics_in_contract_order(self):
        assert TOPIC_IDS == (
            "politics",
            "economy",
            "technology",
            "science-health",
            "identity",
            "society",
            "global",
        )

    def test_taxonomy_dict_shape(self):
        tax = taxonomy_dict()
        assert tax["version"] == TAXONOMY_VERSION == 1
        assert [t["id"] for t in tax["topics"]] == list(TOPIC_IDS)
        for t in tax["topics"]:
            assert set(t) == {"id", "label", "description", "keywords"}
            assert t["label"] and t["description"] and t["keywords"]

    def test_keywords_lowercase_and_unique_per_topic(self):
        for t in TOPICS:
            assert all(k == k.lower().strip() for k in t.keywords), t.id
            assert len(set(t.keywords)) == len(t.keywords), t.id

    def test_every_opinionsqa_coarse_topic_maps(self):
        # The 23 coarse topics of the OpinionsQA release.
        assert len(OPINIONSQA_COARSE_TO_TOPIC) == 23
        assert set(OPINIONSQA_COARSE_TO_TOPIC.values()) == set(TOPIC_IDS)

    def test_site_mirror_matches(self):
        """site/src/lib/topics.ts mirrors the ids and labels defined here."""
        ts = (REPO / "site" / "src" / "lib" / "topics.ts").read_text(encoding="utf-8")
        pairs = re.findall(r'id: "([^"]+)",\s*label: "([^"]+)"', ts)
        assert pairs == [(t.id, t.label) for t in TOPICS]


class TestKeywordFallback:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Did you vote in the last election?", "politics"),
            ("How would you rate the economy and jobs in your area?", "economy"),
            ("How often do you use social media?", "technology"),
            (
                "Would you say your own health is excellent, good, fair, or poor?",
                "science-health",
            ),
            ("How important is religion in your life?", "identity"),
            ("How much is crime a problem in your neighborhood?", "society"),
            ("Is China an ally or a threat?", "global"),
        ],
    )
    def test_basic(self, text, expected):
        assert keyword_topic(text) == expected

    def test_case_insensitive(self):
        assert keyword_topic("WHAT IS YOUR VIEW ON ABORTION?") == "politics"

    def test_no_match_is_none(self):
        assert keyword_topic("What do you think about the situation?") is None
        assert keyword_topic("") is None

    # Substring-bug regressions from the old 10-category classifier.
    def test_discrimination_is_not_nation(self):
        assert keyword_topic("Is there discrimination against them?") == "identity"

    def test_actually_is_not_ally(self):
        assert keyword_topic("Do you actually believe that?") is None

    def test_country_alone_is_not_global(self):
        text = (
            "I am going to name an institution in this country. As far as the "
            "people running this institution are concerned, would you say you "
            "have a great deal of confidence, only some confidence, or hardly "
            "any confidence at all in them? The military"
        )
        assert (
            keyword_topic(text.replace("The military", "Organized labor")) != "global"
        )
        assert keyword_topic("Should divorce in this country be easier?") == "society"

    def test_phrases_match_on_word_boundaries(self):
        assert keyword_topic("Is climate change a threat?") == "science-health"
        assert keyword_topic("Do you trust the  supreme   court?") == "politics"


class TestCommittedLabels:
    @pytest.mark.parametrize("dataset", LABELED_DATASETS)
    def test_label_file_shape(self, dataset):
        data = json.loads((LABELS_DIR / f"{dataset}.json").read_text(encoding="utf-8"))
        assert data["taxonomy_version"] == TAXONOMY_VERSION
        assert data["dataset"] == dataset
        assert data["source"]
        assert data["labels"]
        assert set(data["labels"].values()) <= set(TOPIC_IDS)

    def test_opinionsqa_registry_keys_all_labeled(self):
        """Every OpinionsQA key the benchmark can draw has a committed label."""
        registry = json.loads(
            (REPO / "data" / "question-text-registries" / "opinionsqa.json").read_text(
                encoding="utf-8"
            )
        )
        labels = load_labels("opinionsqa")
        missing = [k for k in registry["questions"] if k not in labels]
        assert missing == []

    @pytest.mark.parametrize("dataset", ("subpop", "gss", "globalopinionqa"))
    def test_current_run_keys_labeled(self, dataset):
        """Every key in the committed leaderboard runs has a label."""
        labels = load_labels(dataset)
        keys: set[str] = set()
        for path in (REPO / "leaderboard-results").glob(f"{dataset}_*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            keys |= {q["key"] for q in data.get("per_question") or [] if q.get("key")}
        assert keys, dataset
        assert sorted(keys - set(labels)) == []

    def test_label_beats_keywords(self):
        # GSS_CONARMY's text mentions "this country" and "the military";
        # its committed label decides, not the keyword fallback.
        label = label_for("gss", "GSS_CONARMY")
        assert label in TOPIC_IDS
        assert topic_for("gss", "GSS_CONARMY", "anything about elections") == label

    def test_dataset_suffix_ignored(self):
        assert load_labels("opinionsqa (2023)") == load_labels("opinionsqa")

    def test_unknown_key_falls_back_to_keywords(self):
        assert topic_for("opinionsqa", "NOT_A_KEY", "Did you vote?") == "politics"
        assert (
            topic_for("ntia", "X", "Do you use the internet at home?") == "technology"
        )
        assert topic_for(None, None, None) is None


class TestCategorizeQuestionCompat:
    def test_returns_labels(self):
        assert categorize_question("Did you vote?") == TOPIC_LABELS["politics"]
        assert categorize_question("nothing here") == FALLBACK_CATEGORY
        assert FALLBACK_CATEGORY in CATEGORIES
        assert len(CATEGORIES) == len(TOPICS) + 1
