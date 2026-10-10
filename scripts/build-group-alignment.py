#!/usr/bin/env python3
"""Build site/src/data/group-alignment.json: per-group match for the Groups page.

For every leaderboard config on SubPOP, OpinionsQA and GlobalOpinionQA,
compare the model's per-question answer distribution with each demographic
group's (or country's) real answer distribution:

    match_g = 100 * (1 - mean_q JSD(model_q, human_q,g))

Each run is scored separately and replicate runs of a config are averaged
per question. Bootstrap over questions (paired across groups) gives 95%
intervals for each group's distance from the config's attribute average,
for the attribute gap (best minus worst group, re-selected in every
resample) and, for ordered attributes, for the last-minus-first contrast.

Model-free reference per group: the whole sample's real answers, which shows
how far each group sits from everyone else. The SubPOP demographic runs also
give, per group, the match with and without the group named in the prompt.

This needs the raw survey data (per-group answers), which CI doesn't have, so
the output is committed. Re-run after adding leaderboard runs:

    synthbench publish-data --results-dir leaderboard-results --output site/src/data/leaderboard.json
    python scripts/build-group-alignment.py

Raw data is read from ~/.synthbench/data (SubPOP raw_rows.json, OpinionsQA
human_resp/*/responses.csv, GlobalOpinionQA questions.json). Systems added
since the last run simply don't appear on the Groups page.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import warnings
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from synthbench.config_id import build_config_id, runnable_ids  # noqa: E402
from synthbench.datasets.globalopinionqa import (  # noqa: E402
    _aggregate_distributions,
    _normalize_options,
    canonical_country,
)
from synthbench.datasets.opinionsqa import OpinionsQADataset  # noqa: E402
from synthbench.datasets.subpop import SUBPOP_ATTRIBUTES, SubPOPDataset  # noqa: E402
from synthbench.metrics.distributional import jensen_shannon_divergence as jsd  # noqa: E402
from synthbench.publish import _tpl_name, is_invalid_run  # noqa: E402

RESULTS = ROOT / "leaderboard-results"
LEADERBOARD = ROOT / "site" / "src" / "data" / "leaderboard.json"
OUT = ROOT / "site" / "src" / "data" / "group-alignment.json"
DATA = Path.home() / ".synthbench" / "data"
B = 500
MIN_COUNTRY_Q = 20
RNG = np.random.default_rng(20261010)
# OpinionsQA answer codes that aren't a group.
SKIP_GROUPS = {"Refused", "Other", "Mixed Race", "In some other way"}

ATTR_LABELS = {
    "POLIDEOLOGY": "Political ideology",
    "POLPARTY": "Party",
    "EDUCATION": "Education",
    "INCOME": "Income",
    "AGE": "Age",
    "RACE": "Race and ethnicity",
    "RELIG": "Religion",
    "CREGION": "Region",
    "SEX": "Sex",
    "COUNTRY": "Country",
}
# Ordered attributes list groups low to high; the rest are nominal.
ORDER = {
    "POLIDEOLOGY": [
        "Very conservative",
        "Conservative",
        "Moderate",
        "Liberal",
        "Very liberal",
    ],
    "POLPARTY": ["Republican", "Independent", "Democrat"],
    "EDUCATION": [
        "Less than high school",
        "High school graduate",
        "Some college, no degree",
        "Associate's degree",
        "College graduate/some postgrad",
        "Postgraduate",
    ],
    "INCOME": [
        "Less than $30,000",
        "$30,000-$50,000",
        "$50,000-$75,000",
        "$75,000-$100,000",
        "$100,000 or more",
    ],
    "AGE": ["18-29", "30-49", "50-64", "65+"],
}
GROUP_LABELS = {
    "College graduate/some postgrad": "College graduate",
    "Some college, no degree": "Some college",
    "Less than $30,000": "Under $30k",
    "$30,000-$50,000": "$30k–50k",
    "$50,000-$75,000": "$50k–75k",
    "$75,000-$100,000": "$75k–100k",
    "$100,000 or more": "$100k or more",
    "Associate's degree": "Associate degree",
    "18-29": "18–29",
    "30-49": "30–49",
    "50-64": "50–64",
}


def norm(d: dict[str, float]) -> dict[str, float]:
    s = sum(max(v, 0.0) for v in d.values())
    return {k: max(v, 0.0) / s for k, v in d.items()} if s > 0 else d


def human_groups() -> dict:
    """{dataset: {attribute: {qkey: {group: dist}}, '_overall': {qkey: dist}}}."""
    out: dict = {}

    sp = SubPOPDataset()
    out["subpop"] = {a: sp.load_demographic_distributions(a) for a in SUBPOP_ATTRIBUTES}
    out["subpop"]["_overall"] = {q.key: q.human_distribution for q in sp.load()}

    # The local OpinionsQA mirror has respondent rows but no per-group JSON,
    # so group distributions are counted from responses.csv (unweighted, the
    # same as the overall NONE_data.json counts SynthBench scores against).
    oq = OpinionsQADataset()
    overall_oq = {q.key: q.human_distribution for q in oq.load()}
    attrs = OpinionsQADataset.DEMOGRAPHIC_ATTRIBUTES
    oq_groups: dict[str, dict] = {a: {} for a in attrs}
    for wave_dir in sorted(
        (DATA / "opinionsqa" / "raw" / "human_resp").glob("American_Trends_Panel_W*")
    ):
        with open(wave_dir / "responses.csv", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            continue
        qcols = [c for c in rows[0] if c in overall_oq]
        for a in attrs:
            if a not in rows[0]:
                continue
            # {group: {question: {option: count}}}
            counts: dict[str, dict[str, dict[str, int]]] = defaultdict(
                lambda: defaultdict(lambda: defaultdict(int))
            )
            for row in rows:
                g = row[a]
                if not g or g in SKIP_GROUPS:
                    continue
                for qk in qcols:
                    if row[qk]:
                        counts[g][qk][row[qk]] += 1
            for g, by_q in counts.items():
                for qk, c in by_q.items():
                    total = sum(c.values())
                    if total < 30:
                        continue
                    oq_groups[a].setdefault(qk, {})[g] = {
                        o: n / total for o, n in c.items()
                    }
    out["opinionsqa"] = oq_groups | {"_overall": overall_oq}

    raw = json.loads(
        (DATA / "globalopinionqa" / "questions.json").read_text(encoding="utf-8")
    )
    countries: dict[str, dict[str, dict[str, float]]] = {}
    overall: dict[str, dict[str, float]] = {}
    for q in raw["questions"]:
        options = _normalize_options(q["options"])
        agg = _aggregate_distributions(q["selections"], options)
        if not agg:
            continue
        overall[q["key"]] = agg
        per: dict[str, dict[str, float]] = {}
        for label, probs in q["selections"].items():
            if len(probs) != len(options) or sum(probs) <= 0:
                continue
            # A country surveyed twice keeps its first sample.
            per.setdefault(canonical_country(label), dict(zip(options, probs)))
        countries[q["key"]] = per
    out["globalopinionqa"] = {"COUNTRY": countries, "_overall": overall}
    return out


def run_config_id(r: dict) -> str:
    cfg = r.get("config", {})
    config_id, _ = build_config_id(
        cfg.get("provider", "unknown"),
        dataset=cfg.get("dataset", "unknown"),
        temperature=cfg.get("temperature"),
        template=_tpl_name(cfg.get("prompt_template")),
        effort=cfg.get("effort"),
        samples_per_question=cfg.get("samples_per_question"),
        question_set_hash=cfg.get("question_set_hash"),
    )
    return config_id


def load_runs(wanted: set[str]) -> dict[str, dict]:
    """config_id -> {dataset, runs: [{qkey: dist}]} for the leaderboard configs."""
    out: dict[str, dict] = {}
    for jf in sorted(RESULTS.glob("*.json")):
        try:
            r = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if r.get("benchmark") != "synthbench" or is_invalid_run(r)[0]:
            continue
        config_id = run_config_id(r)
        if config_id not in wanted:
            continue
        model = {
            pq["key"]: norm(pq["model_distribution"])
            for pq in r.get("per_question", [])
            if pq.get("model_distribution")
        }
        c = out.setdefault(config_id, {"dataset": r["config"]["dataset"], "runs": []})
        c["runs"].append(model)
    return out


def r1(v: float) -> float:
    return round(float(v), 1)


def score_attr(
    runs: list[dict[str, dict[str, float]]], by_q: dict, groups: list[str]
) -> tuple[np.ndarray, list[str]] | None:
    """Questions x groups matrix of 1 - JSD (NaN where the group wasn't asked).

    Each run is scored separately and replicate runs are averaged per
    question, so a config with more runs isn't scored on smoother
    (pooled) answer shares than a config with one.
    """
    keys = sorted({k for run in runs for k in run if k in by_q})
    if not keys:
        return None
    acc = np.zeros((len(keys), len(groups)))
    cnt = np.zeros((len(keys), len(groups)))
    for run in runs:
        for i, k in enumerate(keys):
            if k not in run:
                continue
            for j, g in enumerate(groups):
                h = by_q[k].get(g)
                if h:
                    acc[i, j] += 1.0 - jsd(run[k], norm(h))
                    cnt[i, j] += 1
    with np.errstate(invalid="ignore"):
        return np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan), keys


def summarize(
    m: np.ndarray, groups: list[str], min_n: int, ordered: bool = False
) -> dict | None:
    n = (~np.isnan(m)).sum(axis=0)
    keep = n >= min_n
    if keep.sum() < 2:
        return None
    m = m[:, keep]
    groups = [g for g, k in zip(groups, keep) if k]
    n = n[keep]
    with np.errstate(invalid="ignore"):
        point = np.nanmean(m, axis=0) * 100
    rel = point - point.mean()
    idx = RNG.integers(0, m.shape[0], size=(B, m.shape[0]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        boot = np.stack([np.nanmean(m[i], axis=0) * 100 for i in idx])
    boot_rel = boot - np.nanmean(boot, axis=1, keepdims=True)
    gaps = np.nanmax(boot, axis=1) - np.nanmin(boot, axis=1)
    lo_rel, hi_rel = np.nanpercentile(boot_rel, [2.5, 97.5], axis=0)
    g_lo, g_hi = np.nanpercentile(gaps, [2.5, 97.5])
    best, worst = int(np.argmax(point)), int(np.argmin(point))
    out = {
        "groups": {
            g: [r1(point[j]), r1(rel[j]), r1(lo_rel[j]), r1(hi_rel[j]), int(n[j])]
            for j, g in enumerate(groups)
        },
        "gap": [r1(point[best] - point[worst]), r1(g_lo), r1(g_hi)],
        "best": groups[best],
        "worst": groups[worst],
    }
    if ordered:
        # Signed contrast between the two ends of an ordered attribute
        # (last minus first, e.g. Very liberal minus Very conservative).
        ends = boot[:, -1] - boot[:, 0]
        c_lo, c_hi = np.nanpercentile(ends, [2.5, 97.5])
        out["ends"] = [r1(point[-1] - point[0]), r1(c_lo), r1(c_hi)]
    return out


def main() -> None:
    lb = json.loads(LEADERBOARD.read_text(encoding="utf-8"))
    entries = [
        e
        for e in lb["entries"]
        if e["dataset"] in ("subpop", "opinionsqa", "globalopinionqa")
    ]
    humans = human_groups()
    configs = load_runs({e["config_id"] for e in entries})
    print(
        f"{len(configs)} of {len(entries)} leaderboard configs found", file=sys.stderr
    )

    # Group lists per dataset/attribute, ordered where the attribute is ordinal.
    datasets: dict[str, dict] = {}
    for ds, attrs in humans.items():
        alist = []
        for a, by_q in attrs.items():
            if a == "_overall":
                continue
            seen = sorted({g for gd in by_q.values() for g in gd})
            groups = [g for g in ORDER.get(a, []) if g in seen] or seen
            alist.append(
                {
                    "id": a,
                    "label": ATTR_LABELS.get(a, a.title()),
                    "ordered": a in ORDER,
                    "groups": [
                        {"id": g, "label": GROUP_LABELS.get(g, g)} for g in groups
                    ],
                }
            )
        datasets[ds] = {"attributes": alist}

    systems: dict[str, dict] = {}
    for cid, c in configs.items():
        ds = c["dataset"]
        attrs_out = {}
        for a in datasets[ds]["attributes"]:
            groups = [g["id"] for g in a["groups"]]
            res = score_attr(c["runs"], humans[ds][a["id"]], groups)
            if res is None:
                continue
            min_n = MIN_COUNTRY_Q if a["id"] == "COUNTRY" else 10
            s = summarize(res[0], groups, min_n, a["ordered"])
            if s:
                attrs_out[a["id"]] = s
        systems[cid] = {
            "dataset": ds,
            "n": len(set().union(*c["runs"])),
            "runs": len(c["runs"]),
            "attrs": attrs_out,
        }

    # Whole-sample reference over each dataset's largest question set.
    reference: dict[str, dict] = {}
    for ds in datasets:
        largest = max(
            (c for c in configs.values() if c["dataset"] == ds),
            key=lambda c: len(set().union(*c["runs"])),
        )
        overall = humans[ds]["_overall"]
        ref_model = {
            k: overall[k] for k in set().union(*largest["runs"]) if k in overall
        }
        reference[ds] = {}
        for a in datasets[ds]["attributes"]:
            groups = [g["id"] for g in a["groups"]]
            res = score_attr([ref_model], humans[ds][a["id"]], groups)
            if res is None:
                continue
            s = summarize(
                res[0],
                groups,
                MIN_COUNTRY_Q if a["id"] == "COUNTRY" else 10,
                a["ordered"],
            )
            if s:
                reference[ds][a["id"]] = s

    # Group named in the prompt (SubPOP demographic runs): each run's
    # published conditioned match per group, against the same run's default
    # answers on the same questions. These runs are experiments outside the
    # leaderboard configs, so they're keyed by method + model + temperature
    # and averaged across runs.
    cond_acc: dict[tuple, dict] = {}
    for jf in sorted(RESULTS.glob("subpop_*.json")):
        r = json.loads(jf.read_text(encoding="utf-8"))
        if not r.get("demographic_breakdown") or is_invalid_run(r)[0]:
            continue
        cfg = r["config"]
        method, model_id = runnable_ids(cfg["provider"])
        temp = cfg.get("temperature")
        if temp is None:
            m = re.search(r"t=([0-9.]+)", cfg["provider"])
            temp = float(m.group(1)) if m else None
        key = (method, model_id, temp)
        slot = cond_acc.setdefault(key, {"runs": 0, "vals": defaultdict(list)})
        slot["runs"] += 1
        model = {
            pq["key"]: norm(pq["model_distribution"])
            for pq in r["per_question"]
            if pq.get("model_distribution")
        }
        for attr, results in r["demographic_breakdown"].items():
            by_q = humans["subpop"].get(attr, {})
            for g in results:
                keys = [k for k in model if g["group"] in by_q.get(k, {})]
                if not keys:
                    continue
                default = 1 - float(
                    np.mean([jsd(model[k], norm(by_q[k][g["group"]])) for k in keys])
                )
                slot["vals"][(attr, g["group"])].append(
                    (
                        100 * default,
                        100 * g["p_dist"],
                        100 * g["p_cond"],
                        g["n_questions"],
                    )
                )
    conditioning = []
    for (method, model_id, temp), slot in cond_acc.items():
        attrs: dict[str, dict] = {}
        for (attr, group), vals in slot["vals"].items():
            attrs.setdefault(attr, {})[group] = [
                r1(np.mean([v[0] for v in vals])),
                r1(np.mean([v[1] for v in vals])),
                r1(np.mean([v[2] for v in vals])),
                int(sum(v[3] for v in vals) / len(vals)),
                len(vals),
            ]
        conditioning.append(
            {
                "method": method,
                "model": model_id,
                "temperature": temp,
                "runs": slot["runs"],
                "attrs": attrs,
            }
        )

    # Drop attributes no config scored (e.g. SubPOP POLIDEOLOGY with no data).
    for ds, meta in datasets.items():
        scored = {a for s in systems.values() if s["dataset"] == ds for a in s["attrs"]}
        meta["attributes"] = [a for a in meta["attributes"] if a["id"] in scored]

    OUT.write_text(
        json.dumps(
            {
                "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "bootstrap": B,
                "datasets": datasets,
                "systems": systems,
                "reference": reference,
                "conditioning": conditioning,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
