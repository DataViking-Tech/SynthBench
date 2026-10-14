#!/usr/bin/env python3
"""Search for complementary ensembles, selected on public questions only.

Usage (needs the canonical human distributions locally; see
synthbench.human_distributions):

    python scripts/search-ensembles.py

Scores every 2-, 3- and 4-model equal-weight blend of the current default
systems (newest scoring, no template / temperature / pack variants, no
claude-code harness) on the public questions, then reports the chosen blends
on the private holdout questions. See docs/ensembles.md.


Metrics match `synthbench ensemble`: equal-weight blend, distributions
rounded to 4 dp, JSD (base 2), Kendall tau-b, refusal calibration;
SPS = mean of the three; Index = 100 * (SPS - random) / (ceiling - random).
Selection uses public questions; reported held-out numbers use the private
holdout questions only.
"""

from __future__ import annotations

import itertools
import logging
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")
logging.disable(logging.WARNING)

from synthbench.findings import load_valid_results  # noqa: E402
from synthbench.human_distributions import load_canonical_distributions  # noqa: E402
from synthbench.leaderboard import display_provider_name, provider_framework  # noqa: E402
from synthbench.private_holdout import is_private_holdout  # noqa: E402
from synthbench.publish import _dedup_results  # noqa: E402

DATASETS = ("opinionsqa", "subpop", "gss", "globalopinionqa")
CEIL = {
    "opinionsqa": 0.999518,
    "subpop": 0.995346,
    "globalopinionqa": 0.997219,
    "gss": 0.998784,
}

results, _ = load_valid_results(Path("leaderboard-results"))
deduped = _dedup_results(results)
systems: dict[str, dict[str, dict]] = defaultdict(dict)
random_rows = {}
for r in deduped:
    c = r["config"]
    ds, p = c["dataset"], c["provider"]
    if ds not in DATASETS:
        continue
    if p == "random-baseline":
        random_rows[ds] = {q["key"]: q for q in r["per_question"]}
        continue
    if (
        provider_framework(p) == "baseline"
        or p.startswith("ensemble/")
        or c.get("prompt_template")
        or c.get("persona_pack")
    ):
        continue
    if (
        c.get("temperature") is not None
        or c.get("harness") == "claude-code"
        or (c.get("refusal_detector_version") or 1) < 4
    ):
        continue
    name = display_provider_name(p) + (
        f" via {c['harness']}" if c.get("harness") else ""
    )
    systems[name][ds] = {
        q["key"]: q for q in r["per_question"] if q.get("model_distribution")
    }
systems = {k: v for k, v in systems.items() if len(v) == 4}
names = sorted(systems)
S = len(names)
human = {ds: load_canonical_distributions(ds) or {} for ds in DATASETS}


def build(ds):
    """Arrays for one dataset: M[s,q,o], H[q,o], valid[q,o], refusals, private flag."""
    keys = sorted(
        set.intersection(*(set(systems[n][ds]) for n in names))
        & set(human[ds])
        & set(random_rows[ds])
    )
    opts = []
    for k in keys:
        o = set(human[ds][k])
        for n in names:
            o |= set(systems[n][ds][k]["model_distribution"])
        o |= set(random_rows[ds][k]["model_distribution"])
        opts.append(sorted(o))
    n_opt = max(len(o) for o in opts)
    Q = len(keys)
    M = np.zeros((S + 1, Q, n_opt))  # last row: random baseline
    H = np.zeros((Q, n_opt))
    valid = np.zeros((Q, n_opt), bool)
    mref = np.zeros((S + 1, Q))
    href = np.zeros(Q)
    for qi, (k, o) in enumerate(zip(keys, opts)):
        valid[qi, : len(o)] = True
        H[qi, : len(o)] = [round(human[ds][k].get(x, 0.0), 4) for x in o]
        for si, n in enumerate(names):
            q = systems[n][ds][k]
            M[si, qi, : len(o)] = [q["model_distribution"].get(x, 0.0) for x in o]
            mref[si, qi] = q.get("model_refusal_rate") or 0.0
        rq = random_rows[ds][k]
        M[S, qi, : len(o)] = [rq["model_distribution"].get(x, 0.0) for x in o]
        mref[S, qi] = rq.get("model_refusal_rate") or 0.0
        href[qi] = systems[names[0]][ds][k].get("human_refusal_rate") or 0.0
    priv = np.array([is_private_holdout(ds, k) for k in keys])
    iu = np.triu_indices(n_opt, 1)
    return dict(M=M, H=H, valid=valid, mref=mref, href=href, priv=priv, iu=iu)


DATA = {ds: build(ds) for ds in DATASETS}


def sps_for(blend, bref, d, sel):
    """blend: (n, Q, O) unrounded; bref: (n, Q). Returns SPS (n,) over questions in sel."""
    B = np.round(blend, 4) * d["valid"]
    H = d["H"]
    Bn = B / np.clip(B.sum(-1, keepdims=True), 1e-12, None)
    Hn = H / np.clip(H.sum(-1, keepdims=True), 1e-12, None)
    m = (Bn + Hn) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        kl_h = np.where(Hn > 0, Hn * np.log2(Hn / m), 0.0).sum(-1)
        kl_b = np.where(Bn > 0, Bn * np.log2(Bn / m), 0.0).sum(-1)
    jsd = 0.5 * kl_h + 0.5 * kl_b
    i, j = d["iu"]
    pv = d["valid"][:, i] & d["valid"][:, j]
    sx = np.sign(H[:, i] - H[:, j]) * pv
    sy = np.sign(B[..., i] - B[..., j]) * pv
    num = (sx * sy).sum(-1)
    den = np.sqrt((np.abs(sx).sum(-1)) * (np.abs(sy).sum(-1)))
    with np.errstate(divide="ignore", invalid="ignore"):
        tau = np.where(den > 0, num / den, 0.0)
    rdiff = np.abs(bref - d["href"])
    s = sel
    p_dist = 1 - jsd[..., s].mean(-1)
    p_rank = (1 + tau[..., s].mean(-1)) / 2
    p_ref = np.clip(1 - rdiff[..., s].mean(-1), 0, 1)
    return (p_dist + p_rank + p_ref) / 3


RAND = {}
for ds, d in DATA.items():
    for private in (False, True):
        sel = d["priv"] if private else ~d["priv"]
        RAND[(ds, private)] = float(
            sps_for(d["M"][S][None], d["mref"][S][None], d, sel)[0]
        )


def index_for(combos, private):
    """combos: (n, k) int array. Returns (n, 4) per-dataset Index."""
    out = np.zeros((len(combos), 4))
    for di, ds in enumerate(DATASETS):
        d = DATA[ds]
        sel = d["priv"] if private else ~d["priv"]
        blend = d["M"][combos].mean(1)
        bref = d["mref"][combos].mean(1)
        s = sps_for(blend, bref, d, sel)
        r = RAND[(ds, private)]
        out[:, di] = 100 * (s - r) / (CEIL[ds] - r)
    return out


def evaluate(combos, private, batch=4000):
    parts = [
        index_for(np.array(combos[i : i + batch]), private)
        for i in range(0, len(combos), batch)
    ]
    return np.vstack(parts)


singles = [[i] for i in range(S)]
sp_pub = evaluate(singles, False)
sp_priv = evaluate(singles, True)


# Public per-question JSD vectors for error correlation.
def jsd_vec(si):
    vs = []
    for ds in DATASETS:
        d = DATA[ds]
        B = np.round(d["M"][si], 4) * d["valid"]
        Bn = B / np.clip(B.sum(-1, keepdims=True), 1e-12, None)
        Hn = d["H"] / np.clip(d["H"].sum(-1, keepdims=True), 1e-12, None)
        m = (Bn + Hn) / 2
        with np.errstate(divide="ignore", invalid="ignore"):
            j = 0.5 * np.where(Hn > 0, Hn * np.log2(Hn / m), 0).sum(
                -1
            ) + 0.5 * np.where(Bn > 0, Bn * np.log2(Bn / m), 0).sum(-1)
        vs.append(j[~d["priv"]])
    return np.concatenate(vs)


V = np.array([jsd_vec(i) for i in range(S)])
R = np.corrcoef(V)

print(
    f"{S} candidate systems; public/private questions: "
    + ", ".join(
        f"{ds} {int((~DATA[ds]['priv']).sum())}/{int(DATA[ds]['priv'].sum())}"
        for ds in DATASETS
    )
)
order = np.argsort(-sp_pub.mean(1))
print("\nSingle systems: public Index -> held-out Index | public OQA SubPOP GSS GOQA")
for i in order:
    print(
        f"  {names[i]:44s} {sp_pub[i].mean():6.1f} -> {sp_priv[i].mean():6.1f} | "
        + " ".join(f"{v:6.1f}" for v in sp_pub[i])
    )

allc = {k: list(itertools.combinations(range(S), k)) for k in (2, 3, 4)}
pub = {k: evaluate(allc[k], False) for k in allc}
best_single = int(order[0])
print(
    f"\nBest single (by public): {names[best_single]}  public {sp_pub[best_single].mean():.1f}  held-out {sp_priv[best_single].mean():.1f}"
)


def show(title, combos):
    print(f"\n{title}")
    if not combos:
        return
    priv = evaluate(combos, True)
    pubv = evaluate(combos, False)
    for c, pu, pr in zip(combos, pubv, priv):
        rs = [R[a, b] for a, b in itertools.combinations(c, 2)]
        bm = max(sp_priv[m].mean() for m in c)
        print(
            f"  pub {pu.mean():5.1f} -> held-out {pr.mean():5.1f} [{' '.join(f'{v:5.1f}' for v in pr)}] best member held-out {bm:5.1f}, error r {np.mean(rs):.2f} | {' + '.join(names[m] for m in c)}"
        )


for k in (2, 3, 4):
    top = [allc[k][i] for i in np.argsort(-pub[k].mean(1))[:3]]
    show(f"Top {k}-model blends by public Index:", top)

thr = sp_pub[best_single].mean() - 15
strong = [i for i in range(S) if sp_pub[i].mean() >= thr]
comp3 = sorted(
    itertools.combinations(strong, 3),
    key=lambda c: np.mean([R[a, b] for a, b in itertools.combinations(c, 2)]),
)[:3]
show(
    f"Lowest error correlation among {len(strong)} systems within 15 points of the best (3-model):",
    comp3,
)

spec = tuple(dict.fromkeys(int(np.argmax(sp_pub[:, di])) for di in range(4)))
show("Per-dataset specialists (best public system on each dataset):", [spec])

naive = tuple(int(i) for i in order[:3])
show("Naive rule, the 3 best single systems:", [naive])

# Gain of blending over the best member, held out, for every 3-model combo.
pr3 = evaluate(allc[3], True).mean(1)
bm3 = np.array([max(sp_priv[m].mean() for m in c) for c in allc[3]])
mr3 = np.array(
    [np.mean([R[a, b] for a, b in itertools.combinations(c, 2)]) for c in allc[3]]
)
gain = pr3 - bm3
print(
    f"\nAll {len(allc[3])} 3-model blends, held out: blend beats its best member in {np.mean(gain > 0):.0%}; "
    f"correlation between mean error r and gain over best member: {np.corrcoef(mr3, gain)[0, 1]:.2f}"
)


# ---- Directional complementarity: correlation of signed residuals ----
def resid_vec(si):
    vs = []
    for ds in DATASETS:
        d = DATA[ds]
        B = np.round(d["M"][si], 4) * d["valid"]
        Bn = B / np.clip(B.sum(-1, keepdims=True), 1e-12, None)
        Hn = d["H"] / np.clip(d["H"].sum(-1, keepdims=True), 1e-12, None)
        res = (Bn - Hn)[~d["priv"]][d["valid"][~d["priv"]]]
        vs.append(res)
    return np.concatenate(vs)


RV = np.array([resid_vec(i) for i in range(S)])
RS = np.corrcoef(RV)
mrs3 = np.array(
    [np.mean([RS[a, b] for a, b in itertools.combinations(c, 2)]) for c in allc[3]]
)
qual = np.array([[sp_pub[m].mean() for m in c] for c in allc[3]])
spread = qual.max(1) - qual.mean(1)
X = np.column_stack([np.ones(len(gain)), mrs3, spread])
coef, *_ = np.linalg.lstsq(X, gain, rcond=None)
print(
    f"\nSigned-residual correlation: gain over best member (held out) ~ {coef[0]:.1f} + {coef[1]:.1f} * mean residual r + {coef[2]:.2f} * quality spread"
)
print(
    f"  raw correlation of mean residual r with gain: {np.corrcoef(mrs3, gain)[0, 1]:.2f}; of quality spread with gain: {np.corrcoef(spread, gain)[0, 1]:.2f}"
)

strong = [i for i in range(S) if sp_pub[i].mean() >= sp_pub[best_single].mean() - 20]
print(
    f"\nResidual correlation among the {len(strong)} systems within 20 points of the best (public):"
)
for i in strong:
    print(f"  {names[i][:30]:30s} " + " ".join(f"{RS[i, j]:5.2f}" for j in strong))
compR = sorted(
    itertools.combinations(strong, 3),
    key=lambda c: np.mean([RS[a, b] for a, b in itertools.combinations(c, 2)]),
)[:5]
show(
    "Most complementary 3-model blends by signed residuals (within 20 points of the best):",
    compR,
)
compR4 = sorted(
    itertools.combinations(strong, 4),
    key=lambda c: np.mean([RS[a, b] for a, b in itertools.combinations(c, 2)]),
)[:3]
show("Most complementary 4-model blends by signed residuals:", compR4)
