#!/usr/bin/env python3
"""Build the committed routing-topic labels in src/synthbench/data/topics/.

Usage (needs the raw survey data in ~/.synthbench/data; see DATASETS.md):

    # OpinionsQA: official coarse topics (topic_mapping.npy, first cg entry)
    python scripts/label-topics.py gold

    # Check the model labeler against the OpinionsQA labels on held-out items
    python scripts/label-topics.py validate --n 300

    # Token and cost estimate for a full pass, then the pass itself
    python scripts/label-topics.py estimate --dataset subpop
    python scripts/label-topics.py label --dataset subpop --max-cost 2

The model labeler sends batches of questions to a cheap OpenRouter model at
temperature 0 with a JSON schema that only allows the seven taxonomy ids.
The prompt carries the taxonomy (with the OpinionsQA coarse topics behind
each id) and few-shot examples drawn from the OpinionsQA labels. Responses
are cached in ~/.synthbench/cache/topic-labels/ so a re-run only pays for
questions it has not labeled yet. Needs OPENROUTER_API_KEY.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from synthbench.topics import (  # noqa: E402
    LABELS_DIR,
    OPINIONSQA_COARSE_TO_TOPIC,
    TAXONOMY_VERSION,
    TOPIC_IDS,
    TOPICS,
)

DATA = Path(os.environ.get("SYNTHBENCH_DATA_DIR", Path.home() / ".synthbench" / "data"))
CACHE = Path.home() / ".synthbench" / "cache" / "topic-labels"
OQA_RAW = DATA / "opinionsqa" / "raw" / "human_resp"
MODEL_DATASETS = ("subpop", "gss", "globalopinionqa")

DEFAULT_MODEL = "qwen/qwen3.8-flash"
PROMPT_VERSION = 2
BATCH = 20
SHOTS_PER_TOPIC = 4
SEED = 7
URL = "https://openrouter.ai/api/v1/chat/completions"


# ---------------------------------------------------------------------------
# Question pools
# ---------------------------------------------------------------------------


def load_pool(dataset: str) -> list[dict]:
    """The dataset's full question pool: ``[{key, text, options}]``."""
    path = DATA / dataset / "questions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        {"key": q["key"], "text": q["text"], "options": list(q.get("options") or [])}
        for q in data["questions"]
    ]


def opinionsqa_gold() -> tuple[dict[str, str], list[dict], dict]:
    """``({key: topic}, [{key, text, options}], coverage)`` from topic_mapping.npy.

    The mapping is keyed by ``"<question text> [<opt1>/<opt2>/...]"``, the
    format of the OpinionsQA release. Every key in the per-wave info.csv
    files (the full OpinionsQA question set) is joined on that string.
    """
    import numpy as np

    mapping = np.load(OQA_RAW / "topic_mapping.npy", allow_pickle=True).item()
    rows: dict[str, dict] = {}
    for info in sorted(OQA_RAW.glob("*/info.csv")):
        with open(info, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                options = ast.literal_eval(row["references"])
                rows[row["key"]] = {
                    "key": row["key"],
                    "text": row["question"],
                    "options": list(options),
                }
    labels: dict[str, str] = {}
    unmatched = no_coarse = 0
    for key, q in rows.items():
        entry = mapping.get(f"{q['text']} [{'/'.join(q['options'])}]")
        if entry is None:
            unmatched += 1
            continue
        coarse = entry.get("cg") or []
        if not coarse:
            no_coarse += 1
            continue
        labels[key] = OPINIONSQA_COARSE_TO_TOPIC[coarse[0]]
    pool_keys = {q["key"] for q in load_pool("opinionsqa")}
    coverage = {
        "info_keys": len(rows),
        "labeled": len(labels),
        "unmatched": unmatched,
        "no_coarse_topic": no_coarse,
        "pool": len(pool_keys),
        "pool_labeled": len(pool_keys & set(labels)),
    }
    questions = [rows[k] for k in sorted(rows)]
    return labels, questions, coverage


def write_labels(dataset: str, labels: dict[str, str], source: str) -> Path:
    LABELS_DIR.mkdir(parents=True, exist_ok=True)
    path = LABELS_DIR / f"{dataset}.json"
    payload = {
        "taxonomy_version": TAXONOMY_VERSION,
        "dataset": dataset,
        "source": source,
        "labels": dict(sorted(labels.items())),
    }
    path.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


def _coarse_by_topic() -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for coarse, tid in OPINIONSQA_COARSE_TO_TOPIC.items():
        out[tid].append(coarse)
    return out


def _fmt_question(q: dict, max_opts: int = 8) -> str:
    opts = [o for o in q["options"] if o.lower() not in ("refused", "dk/refused")]
    shown = "; ".join(opts[:max_opts]) + ("; ..." if len(opts) > max_opts else "")
    return f"{q['text'].strip()}\n   Options: {shown}"


def few_shot(gold: dict[str, str], questions: list[dict]) -> list[dict]:
    """Fixed-seed few-shot examples, ``SHOTS_PER_TOPIC`` per topic."""
    rng = random.Random(SEED)
    by_topic: dict[str, list[dict]] = defaultdict(list)
    for q in questions:
        if q["key"] in gold:
            by_topic[gold[q["key"]]].append(q)
    shots = []
    for tid in TOPIC_IDS:
        pool = sorted(by_topic[tid], key=lambda q: q["key"])
        for q in rng.sample(pool, min(SHOTS_PER_TOPIC, len(pool))):
            shots.append({**q, "topic": tid})
    rng.shuffle(shots)
    return shots


def system_prompt(shots: list[dict]) -> str:
    coarse = _coarse_by_topic()
    lines = [
        "You label survey questions with one topic from a fixed list.",
        "Pick the topic the question is mainly about. Label by subject, not by",
        "the answer format. 'global' is for foreign policy, views of other",
        "countries or world leaders, and relations between countries. Surveys",
        "are run in many countries: a question about the respondent's own",
        "country (its government, elections, economy, schools, religion) gets",
        "the topic of that subject, not 'global'. Questions about trust in an",
        "institution go to the topic of that institution (news media ->",
        "technology, scientists -> science-health, Congress -> politics, banks",
        "or companies -> technology).",
        "",
        "Topics:",
    ]
    for t in TOPICS:
        lines.append(f"- {t.id}: {t.description} (covers: {'; '.join(coarse[t.id])})")
    lines += ["", "Examples:"]
    for i, s in enumerate(shots, 1):
        lines.append(f"{i}. {_fmt_question(s)}\n   Topic: {s['topic']}")
    lines += [
        "",
        'Reply with JSON: {"labels": [{"i": <question number>, "topic": <topic id>}]}',
        "with one entry per question, in order.",
    ]
    return "\n".join(lines)


def user_prompt(batch: list[dict]) -> str:
    body = "\n".join(f"{i}. {_fmt_question(q)}" for i, q in enumerate(batch, 1))
    return f"Label each question.\n\n{body}"


SCHEMA = {
    "name": "topic_labels",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "labels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "i": {"type": "integer"},
                        "topic": {"type": "string", "enum": list(TOPIC_IDS)},
                    },
                    "required": ["i", "topic"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["labels"],
        "additionalProperties": False,
    },
}


# ---------------------------------------------------------------------------
# OpenRouter calls with a per-question cache
# ---------------------------------------------------------------------------


class Labeler:
    def __init__(self, model: str, shots: list[dict], workers: int = 8):
        self.model = model
        self.system = system_prompt(shots)
        self.workers = workers
        self.cost = 0.0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        tag = hashlib.sha256(
            f"{model}|{PROMPT_VERSION}|{self.system}".encode()
        ).hexdigest()[:12]
        self.cache_path = CACHE / f"{model.replace('/', '_')}-{tag}.json"
        self.cache: dict[str, str] = (
            json.loads(self.cache_path.read_text(encoding="utf-8"))
            if self.cache_path.is_file()
            else {}
        )

    @staticmethod
    def _ckey(dataset: str, q: dict) -> str:
        return f"{dataset}:{q['key']}"

    def save(self) -> None:
        CACHE.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self.cache, indent=0), encoding="utf-8")

    def _call(self, batch: list[dict]) -> tuple[list[str | None], dict]:
        import httpx

        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            sys.exit("OPENROUTER_API_KEY is not set")
        body = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": self.system},
                {"role": "user", "content": user_prompt(batch)},
            ],
            "response_format": {"type": "json_schema", "json_schema": SCHEMA},
            "reasoning": {"enabled": False},
            "usage": {"include": True},
            "max_tokens": 40 * len(batch) + 100,
        }
        for attempt in range(4):
            try:
                r = httpx.post(
                    URL,
                    headers={"Authorization": f"Bearer {key}"},
                    json=body,
                    timeout=120,
                )
                r.raise_for_status()
                data = r.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)["labels"]
                out: list[str | None] = [None] * len(batch)
                for item in parsed:
                    i = int(item["i"]) - 1
                    if 0 <= i < len(batch) and item["topic"] in TOPIC_IDS:
                        out[i] = item["topic"]
                return out, data.get("usage") or {}
            except Exception as exc:  # noqa: BLE001 - retry any transport/parse error
                if attempt == 3:
                    print(f"  batch failed: {exc}", file=sys.stderr)
                    return [None] * len(batch), {}
                time.sleep(2 * (attempt + 1))
        return [None] * len(batch), {}

    def label(self, dataset: str, questions: list[dict]) -> dict[str, str]:
        todo = [q for q in questions if self._ckey(dataset, q) not in self.cache]
        batches = [todo[i : i + BATCH] for i in range(0, len(todo), BATCH)]
        if batches:
            print(f"  {len(todo)} uncached questions in {len(batches)} calls")
        with ThreadPoolExecutor(self.workers) as pool:
            for batch, (labels, usage) in zip(batches, pool.map(self._call, batches)):
                self.cost += float(usage.get("cost") or 0.0)
                self.prompt_tokens += int(usage.get("prompt_tokens") or 0)
                self.completion_tokens += int(usage.get("completion_tokens") or 0)
                for q, lab in zip(batch, labels):
                    if lab:
                        self.cache[self._ckey(dataset, q)] = lab
        self.save()
        return {
            q["key"]: self.cache[self._ckey(dataset, q)]
            for q in questions
            if self._ckey(dataset, q) in self.cache
        }


def estimate(system: str, questions: list[dict], model: str) -> dict:
    """Rough token/cost estimate (4 characters per token) from model pricing."""
    import httpx

    n_calls = -(-len(questions) // BATCH)
    sys_tokens = len(system) / 4
    q_tokens = sum(len(user_prompt([q])) for q in questions) / 4
    prompt = n_calls * sys_tokens + q_tokens
    completion = len(questions) * 12 + n_calls * 10
    pricing = {}
    try:
        models = httpx.get("https://openrouter.ai/api/v1/models", timeout=30).json()[
            "data"
        ]
        pricing = next(m["pricing"] for m in models if m["id"] == model)
    except Exception:  # noqa: BLE001
        pass
    cost = prompt * float(pricing.get("prompt", 0)) + completion * float(
        pricing.get("completion", 0)
    )
    return {
        "questions": len(questions),
        "calls": n_calls,
        "prompt_tokens": int(prompt),
        "completion_tokens": int(completion),
        "est_cost_usd": round(cost, 4),
    }


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


_GOLD_SOURCE = (
    "OpinionsQA topic_mapping.npy (Santurkar et al. 2023): first coarse "
    "topic (cg) mapped to the routing taxonomy; joined on question text "
    "plus options"
)


def cmd_gold(args) -> None:
    labels, questions, coverage = opinionsqa_gold()
    source = _GOLD_SOURCE
    if args.fill_missing:
        # The few OpinionsQA questions with no coarse topic get a model label.
        missing = [q for q in questions if q["key"] not in labels]
        labeler = Labeler(args.model, _shots(), workers=args.workers)
        filled = labeler.label("opinionsqa", missing)
        labels.update(filled)
        coverage["model_filled"] = len(filled)
        source += (
            f"; {len(filled)} questions with no coarse topic labeled by "
            f"{args.model} (scripts/label-topics.py)"
        )
        print(f"cost ${labeler.cost:.4f}")
    path = write_labels("opinionsqa", labels, source)
    print(json.dumps(coverage, indent=1))
    print(f"wrote {path} ({len(labels)} labels)")
    print(dict(Counter(labels.values())))


def _validation_split(n: int) -> tuple[list[dict], list[dict], dict[str, str]]:
    gold, questions, _ = opinionsqa_gold()
    shots = few_shot(gold, questions)
    shot_stems = {s["text"][:60] for s in shots}
    rng = random.Random(SEED + 1)
    pool = [
        q
        for q in questions
        if q["key"] in gold
        and q["key"] not in {s["key"] for s in shots}
        and q["text"][:60] not in shot_stems
    ]
    return shots, rng.sample(pool, min(n, len(pool))), gold


def cmd_validate(args) -> None:
    shots, sample, gold = _validation_split(args.n)
    labeler = Labeler(args.model, shots, workers=args.workers)
    if args.estimate_only:
        print(json.dumps(estimate(labeler.system, sample, args.model), indent=1))
        return
    pred = labeler.label("opinionsqa-validate", sample)
    agree = sum(1 for q in sample if pred.get(q["key"]) == gold[q["key"]])
    total = sum(1 for q in sample if q["key"] in pred)
    print(
        f"agreement {agree}/{total} = {agree / max(total, 1):.1%} (missing {len(sample) - total})"
    )
    confusion = Counter(
        (gold[q["key"]], pred[q["key"]])
        for q in sample
        if q["key"] in pred and pred[q["key"]] != gold[q["key"]]
    )
    for (g, p), c in confusion.most_common(12):
        print(f"  gold {g:15} -> pred {p:15} x{c}")
    print(
        f"cost ${labeler.cost:.4f} ({labeler.prompt_tokens} prompt + "
        f"{labeler.completion_tokens} completion tokens)"
    )


def _shots() -> list[dict]:
    gold, questions, _ = opinionsqa_gold()
    return few_shot(gold, questions)


def cmd_estimate(args) -> None:
    labeler = Labeler(args.model, _shots())
    for ds in args.dataset:
        pool = load_pool(ds)
        todo = [q for q in pool if Labeler._ckey(ds, q) not in labeler.cache]
        print(ds, json.dumps(estimate(labeler.system, todo, args.model)))


def cmd_label(args) -> None:
    labeler = Labeler(args.model, _shots(), workers=args.workers)
    pools = {ds: load_pool(ds) for ds in args.dataset}
    todo = [
        q
        for ds, pool in pools.items()
        for q in pool
        if Labeler._ckey(ds, q) not in labeler.cache
    ]
    est = estimate(labeler.system, todo, args.model)
    print(f"estimate for {len(todo)} uncached questions: {json.dumps(est)}")
    if est["est_cost_usd"] > args.max_cost:
        sys.exit(f"estimated ${est['est_cost_usd']} exceeds --max-cost {args.max_cost}")
    for ds, pool in pools.items():
        labels = labeler.label(ds, pool)
        missing = len(pool) - len(labels)
        path = write_labels(
            ds,
            labels,
            f"model labeler: {args.model}, temperature 0, prompt v{PROMPT_VERSION}, "
            f"{SHOTS_PER_TOPIC} OpinionsQA examples per topic (scripts/label-topics.py)",
        )
        print(f"{ds}: {len(labels)}/{len(pool)} labeled (missing {missing}) -> {path}")
        print("  ", dict(Counter(labels.values())))
    print(
        f"cost this run ${labeler.cost:.4f} ({labeler.prompt_tokens} prompt + "
        f"{labeler.completion_tokens} completion tokens)"
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gold")
    g.add_argument("--fill-missing", action="store_true")
    g.set_defaults(func=cmd_gold)

    v = sub.add_parser("validate")
    v.add_argument("--n", type=int, default=300)
    v.add_argument("--estimate-only", action="store_true")
    v.set_defaults(func=cmd_validate)

    e = sub.add_parser("estimate")
    e.add_argument("--dataset", nargs="+", default=list(MODEL_DATASETS))
    e.set_defaults(func=cmd_estimate)

    lab = sub.add_parser("label")
    lab.add_argument("--dataset", nargs="+", default=list(MODEL_DATASETS))
    lab.add_argument("--max-cost", type=float, default=2.0)
    lab.set_defaults(func=cmd_label)

    for p in (g, v, e, lab):
        p.add_argument("--model", default=DEFAULT_MODEL)
    for p in (g, v, lab):
        p.add_argument("--workers", type=int, default=8)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
