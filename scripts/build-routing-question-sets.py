#!/usr/bin/env python3
"""Build the ``routing`` suite: one pinned question set per core dataset.

routing.json ranks systems per (slice, topic), and a topic needs roughly 30+
questions before a lead over the runner-up can show. The default 100-question
runs leave most topics far below that. Each set here keeps the first 100
questions (the ones every published 100-question run already answered) and
tops every routing topic up to ``PER_TOPIC`` questions from the rest of the
pool, in the dataset's own order. Datasets whose whole pool is small enough
(OpinionsQA's 684, GSS's 75) use the whole pool.

Output: ``src/synthbench/suites/routing/<dataset>.json``. Run a system on it
with ``synthbench run ... --suite routing``.

Needs the dataset caches under ~/.synthbench/data (same as ``synthbench run``).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from synthbench.datasets import DATASETS
from synthbench.topics import TOPIC_IDS, load_labels

OUT_DIR = Path(__file__).resolve().parent.parent / "src/synthbench/suites/routing"
BASE = 100
PER_TOPIC = 75
WHOLE_POOL = {"opinionsqa", "gss"}
DATASETS_IN_INDEX = ("opinionsqa", "gss", "subpop", "globalopinionqa")


def build(dataset: str) -> dict:
    keys = [q.key for q in DATASETS[dataset]().load()]
    labels = load_labels(dataset)
    if dataset in WHOLE_POOL:
        chosen = keys
        rule = "whole pool"
    else:
        chosen = keys[:BASE]
        have = Counter(labels.get(k) for k in chosen)
        for k in keys[BASE:]:
            topic = labels.get(k)
            if topic is not None and have[topic] < PER_TOPIC:
                chosen.append(k)
                have[topic] += 1
        rule = f"first {BASE}, then each topic topped up to {PER_TOPIC} in pool order"
    counts = Counter(labels.get(k) for k in chosen)
    return {
        "suite": "routing",
        "dataset": dataset,
        "description": f"Question set for routing.json ({rule}).",
        "n": len(chosen),
        "topic_counts": {t: counts.get(t, 0) for t in TOPIC_IDS},
        "keys": chosen,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS_IN_INDEX:
        payload = build(dataset)
        path = OUT_DIR / f"{dataset}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"{dataset}: {payload['n']} questions {payload['topic_counts']}")


if __name__ == "__main__":
    main()
