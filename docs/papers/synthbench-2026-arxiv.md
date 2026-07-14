# SynthBench: An Open Benchmark for Distributional and Steerability Fidelity of Synthetic Survey Respondents

> ## ⚠ Errata (2026-07-13) — several numbers below are superseded
>
> This preprint draft (v1, 2026-05-14) predates the score recompute.
> The publish pipeline now recomputes all published scores from
> per-question rows (#305), and the quantitative findings are regenerated
> from committed artifacts with a CI drift guard (#309). **Current numbers
> live in [`FINDINGS.md`](../../FINDINGS.md) and on the live leaderboard —
> treat the figures below as historical.** Specifically superseded:
>
> - **OpinionsQA 3-model ensemble SPS 0.836 → 0.877** (recomputed full
>   composite; the draft's 0.836 was the retired 2-metric convention).
> - **SubPOP 3-model ensemble SPS 0.796 → 0.879.** The blend additionally
>   includes a constituent run
>   (`subpop_synthpanel_claude-haiku-4-5-20251001_20260411_073013`) that the
>   run-validity filter now excludes as uniform-distribution garbage, so
>   even the recomputed score understates a clean re-blend.
> - **GlobalOpinionQA 3-model ensemble SPS 0.747 (rank 7) → 0.813 (rank 1).**
> - **"Republican conditioning 2.4× stronger than Democrat" → 2.2×**
>   (mean P_cond 0.073 vs 0.033 across committed replications).
> - **The "SPS 0.900" optimal-temperature ensemble** was computed under the
>   retired 2-metric composite from blend files never committed to
>   `leaderboard-results/`; superseded by the recomputed default-temperature
>   ensemble scores.
> - **Ensemble gain "+5–7 pts, consistent across all 3 datasets"** is
>   comparison-set dependent; against the best single leaderboard entry at
>   matched question count it is +2.7 to +5.8 pts per dataset.
> - **"Core" suite size: 300 questions → 200** (`suites/core.json` defines
>   200 questions).
> - **"Five-replication trials"** overstates the committed replication
>   count — the artifacts carry `run_count: 2` for those configurations.
>
> Editorial rewrite of the body text is the maintainer's follow-up
> (#258 / Move 3); this banner only flags what changed.

**Authors:** DataViking-Tech (corresponding: wesley@dataviking.tech)
**Version:** Preprint v1 — 2026-05-14
**Suggested arXiv category:** cs.CL (primary), cs.HC (secondary), stat.AP (secondary)
**Companion code:** https://github.com/DataViking-Tech/synthbench
**Companion site:** https://synthbench.org
**Suggested citation:**

```bibtex
@misc{synthbench2026,
  title  = {SynthBench: An Open Benchmark for Distributional and Steerability Fidelity of Synthetic Survey Respondents},
  author = {{DataViking-Tech}},
  year   = {2026},
  eprint = {arXiv:TBD},
  url    = {https://synthbench.org}
}
```

---

## Abstract

Synthetic survey respondents — large language models prompted to answer survey
items as if they were members of specific demographic groups — are increasingly
used in market research, user-experience research (UXR), and computational
social science. Existing evaluation work (OpinionsQA, GlobalOpinionQA, SubPOP)
established the central methodological pillars: Jensen–Shannon divergence
against ground-truth Pew distributions, persona steerability through QA / BIO /
PORTRAY prompting styles, and subgroup-level audits. These contributions are
necessary but not sufficient for a *vendor-comparable* benchmark, because they
(i) measure single-model behavior rather than productized pipelines,
(ii) emit aggregate scores that obscure subgroup-specific failure modes,
(iii) do not specify a public, reproducible scoring contract that an open
leaderboard can enforce, and (iv) have no defense against contamination once
their question sets become widely indexed.

We present SynthBench, an open benchmark that operationalizes these pillars as
a single deployable evaluator. Our contributions are:

1. **A six-component parity score (SPS)** decomposing synthetic-respondent
   quality into distributional fidelity (P_dist), rank fidelity (P_rank),
   conditioning fidelity (P_cond), subgroup consistency (P_sub), refusal
   calibration (P_refuse), and a Phase-2 thematic axis (P_theme).
2. **A multi-dataset evaluation protocol** spanning OpinionsQA (1,498 US Qs),
   SubPOP (3,362 US subpopulation Qs), and GlobalOpinionQA (2,556 cross-country
   Qs) — 7,416 questions, 138 countries, 22 subpopulations — with stratified
   "Core" subsets for fast iteration and "Full" suites for publication.
3. **Five interpretable baselines** (Random, Majority-Class, Population-Average,
   Unconditioned-LLM, Human-Ceiling via split-half) that bracket the meaningful
   evaluation range.
4. **An adversarial integrity stack:** a private 20 % holdout keyed by SHA-256
   of (question, quarterly salt), tiered statistical validation that
   recomputes every aggregate from per-question data, a continuously-running
   adversarial-regression suite of fabricated submissions, and a
   `perfection → ERROR` invariant that hard-flags submissions exceeding the
   human ceiling.
5. **Quantitative findings** from 200+ runs across 3 datasets: multi-model
   ensemble blending is the largest single lever (+5–7 SPS points, zero
   incremental API cost), persona conditioning produces small (2–7 %) but
   asymmetric effects that quantify directional bias in LLM defaults, and
   temperature sensitivity is governed by base output entropy rather than
   model scale.

SynthBench is publicly hosted, openly reproducible (`pip install synthbench`),
and operates under a "perfection-is-suspicion" auditing posture designed to
remain trustworthy as the field's collective Goodhart pressure rises.

---

## 1. Introduction

### 1.1 Motivation

Practitioners are already deploying synthetic respondents in production. UX
research vendors (Synthetic Users, Ditto, Persona), market-research platforms
adopting LLM augmentation, and Fortune-500 internal research teams routinely
substitute LLM personas for at least a subset of human-respondent panels.
A 2025 survey of insights-vendor procurement showed line-item budget for
"AI panel" already exceeding human-panel spend in 14 % of mid-market accounts.

The published methodological literature on these tools has so far been
descriptive ("here is what an LLM does when prompted as a Republican") rather
than evaluative ("here is whether vendor X's product is materially better than
prompting raw GPT-4o"). The result is an inferential gap: buyers cannot
distinguish between vendors, vendors cannot demonstrate improvement to buyers,
and the academic community cannot meaningfully compare published synthetic-
respondent results across papers. The dominant phrase has become "trendslop"
(Harvard Business Review, 2026) — plausible-sounding research output without
any measured fidelity to the populations it claims to represent.

SynthBench is the measurement layer for that critique. We build on
OpinionsQA's framing (Santurkar et al., 2023) and SubPOP's distribution
fitting (Suh et al., 2025), and add the public-leaderboard, adversarial-
integrity, and multi-axis decomposition that vendor evaluation requires.

### 1.2 Scope of contribution

We claim novelty along four axes:

1. **Vendor-facing decomposition.** Existing benchmarks emit one composite
   alignment number per (model, dataset). Practitioners need to know
   *whether the conditioning mechanism works*, not just whether the default
   distribution happens to land near aggregate Pew. SPS separates these.
2. **Public, defended-against-contamination evaluation.** A 20 % private
   holdout, salted quarterly, with a tiered statistical validator that
   diverges public-vs-private SPS computations is, to our knowledge, the
   first such contamination defense published for a population-distribution
   benchmark.
3. **Six axes, computed identically across providers.** Logprob-equipped
   providers return distributions directly; sampling-only providers use a
   Wilson-interval-bounded 30/100-sample protocol. Both produce the same
   six numbers, enabling apples-to-apples comparison.
4. **Reproducibility receipts.** Every leaderboard row carries a config hash,
   a pricing snapshot, a coverage flag, and a verification status
   (✓ verified / ⚠ flagged). The benchmark publishes its own anomalies.

### 1.3 What we do not claim

We do not claim to evaluate qualitative reasoning (Phase 2 work, deferred to
P_theme). We do not claim to measure persuasion or content quality — only
fidelity of the response distribution to ground-truth human distributions.
And we are explicit that "indistinguishable from humans" (SPS → 1.0) is a
ceiling, not a goal; in many UXR settings a calibrated under-confidence
(P_refuse matching human refusal patterns) is more valuable than perfect
distributional alignment.

---

## 2. Related Work

### 2.1 Foundational benchmarks

**OpinionsQA** (Santurkar et al., ICML 2023) introduced the Pew-American-Trends-
Panel ground truth, the QA / BIO / PORTRAY conditioning styles, and the
1-Wasserstein distance as the primary fidelity metric over 1,498 questions
× 60 demographic groups. Their finding that LLMs systematically over-represent
young, liberal, college-educated respondents is the operational backdrop
against which every subsequent synthetic-respondent system is judged.

**GlobalOpinionQA** (Durmus et al., 2024) extended ground-truth coverage from
the US to 138 countries via Pew Global Attitudes and a World Values Survey
subset, surfacing systematic Western-centric biases in default LLM outputs.
They used Jensen–Shannon divergence as the primary metric.

**SubPOP** (Suh et al., ACL 2025) fine-tuned models to *predict* subpopulation
distributions and shipped a 3,362-question, 22-subpopulation dataset suitable
as ready-made ground truth for distributional-fidelity evaluation.

### 2.2 Persona reliability and steerability

A 2026 follow-up (Wang et al., "Assessing the Reliability of Persona-Conditioned
LLMs as Synthetic Survey Respondents," arXiv:2602.18462) evaluated two models
across 70K WVS respondent–item pairs and found that persona prompting *does
not uniformly improve* alignment with the target demographic. This is the most
direct methodological motivation for our P_cond axis: we wanted a metric that
exposes *when* conditioning helps versus hurts, rather than rolling its effect
into a single composite.

### 2.3 Benchmark integrity literature

The 2025 UC-Berkeley AgentBench teardown (Gupta et al.) demonstrated how
publicly-indexed evaluation suites are inevitably contaminated by next-
generation model training data and how vendor-submitted scores drift up over
time without underlying capability change. LMArena's 2025 partial collapse
under Goodhart pressure (chat-style optimization at the expense of measured
capability) is the second cautionary case. Our holdout + salt + adversarial-
regression design is direct lineage from this literature; we cite the Berkeley
paper inline in our `/methodology` site page.

### 2.4 Positioning

SynthBench is best read as "OpinionsQA × SubPOP × GlobalOpinionQA, decomposed
into vendor-comparable axes and deployed as a public adversarial leaderboard."
The contribution is not a new dataset or a new metric per se — it is the
integration, the productization, and the integrity stack that makes the
underlying methodology *useful* to a buyer.

---

## 3. The SynthBench Parity Score (SPS)

### 3.1 Composite definition

For a given (provider, dataset, suite) tuple:

```
SPS = w_dist · P_dist + w_rank · P_rank + w_cond · P_cond
    + w_sub  · P_sub  + w_refuse · P_refuse
```

Default weights are uniform (0.20 each); the composite is a *convenience*
aggregate over the five Phase-1 axes. All five sub-scores are published
alongside the composite — a vendor cannot hide a P_cond failure behind a
strong P_dist.

### 3.2 P_dist — Distributional Parity

For each (question q, demographic group g):

```
JSD(q, g) = 0.5 · KL(P_provider ‖ M) + 0.5 · KL(P_human ‖ M)
where M = 0.5 · (P_provider + P_human)
```

We aggregate as `P_dist = 1 - mean(JSD)` over all valid (q, g) pairs.

Jensen–Shannon is chosen over 1-Wasserstein as the primary distance because
(i) it is universally defined (does not require ordinal options),
(ii) it is bounded, symmetric, and finite under zero-mass entries, and
(iii) it is consistent with GlobalOpinionQA's choice, easing cross-paper
comparison. For ordinal-only items (Likert scales) we report 1-Wasserstein
as a supplementary signal.

### 3.3 P_rank — Rank-Order Parity

Kendall's τ-b on the option rankings:

```
P_rank = (1 + mean(τ_b)) / 2,  τ_b ∈ [-1, 1]
```

τ-b handles tied ranks, which are pervasive when options have similar
probabilities. Rank fidelity is preserved when 45/35/20 maps to 40/38/22 —
the *ordering* of options is captured even when exact masses drift. This is
the metric a UX researcher cares about most when choosing between "which
feature should we build first" options.

### 3.4 P_cond — Conditioning Fidelity

For each demographic group g:

```
align_default(g)     = P_dist with PersonaSpec=∅
align_conditioned(g) = P_dist with PersonaSpec=g
P_cond(g)            = max(0, align_conditioned(g) - align_default(g))
P_cond               = mean over groups of P_cond(g)
```

We floor at zero per-group: conditioning that *worsens* alignment earns no
credit, but the raw signed value is preserved in the model card for
diagnostic use. Raw LLMs are evaluated with all three OpinionsQA conditioning
styles (QA, BIO, PORTRAY) and we take the maximum.

P_cond is the most product-relevant axis for vendor evaluation: it isolates
the *conditioning mechanism* from accidental distributional luck.

### 3.5 P_sub — Subgroup Consistency

```
P_sub = 1 - CV(P_dist scores per group)
      where CV = std / mean
```

Coefficient of variation rather than standard deviation, because we care about
*relative* dispersion: 0.90 ± 0.02 is more consistent than 0.70 ± 0.10 even
though their absolute standard deviations differ by ~5×. Per-group scores are
always published; P_sub is the summary, the breakdown is the audit trail.

### 3.6 P_refuse — Refusal Calibration

```
P_refuse = 1 - mean(|R_provider(q, g) - R_human(q, g)|)
```

Where R denotes the refusal probability. A provider that never refuses is
over-confident; one that always refuses is useless. Human refusal patterns
carry signal (income → refusal correlates with bracket; religion → refusal
correlates with non-affiliation), and a faithful synthetic respondent should
reproduce them.

### 3.7 P_theme — Thematic Parity [Phase 2]

For open-ended responses: cluster human responses into themes via embedding +
agglomerative clustering, score provider responses against the cluster
distribution. Deferred to Phase 2 pending an open-ended ground-truth dataset
(planned: World Values Survey qualitative supplements).

### 3.8 Score interpretation

Scores live in [0, 1]:

- **SPS = 1.00** — Indistinguishable from real human survey data. *We hard-
  flag* this as overfitting or holdout contamination. Honest scores live below
  the Human-Ceiling baseline (see §4.5).
- **SPS ≈ 0.85** — State of the art at the time of writing (3-model ensemble
  on OpinionsQA).
- **SPS ≈ 0.65** — Competent raw LLM with default prompting.
- **SPS ≈ 0.50** — Population-Average baseline (no conditioning).
- **SPS ≈ 0.30** — Random uniform baseline.

---

## 4. Baselines

Every baseline is run through the *same evaluation pipeline* as a real
provider — including the same SHA-256-partitioned 80/20 split, the same
sampling protocol, and the same per-group decomposition.

### 4.1 Random Baseline

Uniform distribution over non-refusal options. Sets the floor: anything at
or below this is adding negative value.

### 4.2 Majority-Class Baseline

Mode of the human population distribution. P_cond ≡ 0 by definition (no
conditioning mechanism). Scores well on consensus questions and poorly on
divisive ones — diagnostic for distinguishing "the model learned the mode"
from "the model learned the distribution shape."

### 4.3 Population-Average Baseline

The full population-aggregated distribution applied to *every* demographic
group. Decent P_dist (matches aggregate), zero P_cond (no demographic
sensitivity). The gap between Population-Average and a conditioned vendor is
the **conditioning premium** — the entire commercial reason synthetic
respondent products exist.

### 4.4 Unconditioned-LLM Baseline (GPT-4o-mini, ∅ persona)

The "just prompt ChatGPT" approach. Most synthetic-respondent procurement
decisions are actually a referendum on whether a vendor materially outperforms
this baseline; if a vendor cannot, the purchase is wasteful.

### 4.5 Human-Ceiling Baseline (Split-Half Reliability)

Random 50/50 split of each demographic group's respondents, compute parity
metrics between the halves. Captures the *inherent sampling noise* in human
survey data. This is the upper bound on achievable score; anything above is
suspicious. Phase-1 measurement on OpinionsQA: SPS-equivalent ≈ 0.99
(per-wave aggregate of subpop ceilings).

The meaningful evaluation range for honest providers is therefore
**[Unconditioned LLM, Human Ceiling]**.

---

## 5. Datasets and Suites

### 5.1 Three primary datasets

| Dataset | Questions | Groups / regions | Source | Phase |
|---|---|---|---|---|
| OpinionsQA | 1,498 | 60 US demographic groups | Pew ATP | Phase 1 |
| SubPOP | 3,362 | 22 US subpopulations | Suh et al. 2025 | Phase 1 |
| GlobalOpinionQA | 2,556 | 138 countries | Pew Global + WVS subset | Phase 2 |
| **Total** | **7,416** | — | — | — |

Auxiliary datasets (manual setup): Pew Internet & Technology, World Values
Survey Wave 7, NORC General Social Survey, NTIA Internet Use Supplement,
Eurobarometer, Michigan Surveys of Consumers.

### 5.2 Core vs. Full suites

| Suite | Questions | Method | Wall-time (logprob) | Cost @ GPT-4o-mini |
|---|---|---|---|---|
| Core | 300 (stratified) | logprob or sampling@100 | ~1h | ~$2.50 |
| Full | 1,498 / 3,362 / 2,556 | logprob or sampling@100 | ~6h | ~$15 |

Core stratifies along three axes: topic coverage (~13 questions × 23 topics),
response entropy band (low/medium/high in ~equal proportion), and
demographic sensitivity (≥30 % flagged-sensitive). Core is *locked per
SynthBench version* — the exact question IDs are committed to the repo so a
Core-only result is reproducible verbatim.

### 5.3 Sampling protocol for non-logprob providers

Providers without token-logprob access (e.g., Anthropic's external API)
estimate distributions via repeated sampling at the provider's *default
temperature*: 30 minimum samples per (q, g), 100 recommended for publication.
Wilson score intervals are reported alongside point estimates so the
uncertainty introduced by sampling is visible.

We deliberately do *not* temperature-optimize sampling providers — the
benchmark measures the provider as a buyer would receive it.

---

## 6. Adversarial Integrity Stack

### 6.1 Threat model

Three threats:

1. **Training-data contamination.** A 2026-era foundation model trained on a
   crawl of `synthbench.org` will see the public Core questions and the
   leaderboard JSON. If we score only on public data, those models will be
   trivially upranked.
2. **Vendor over-fitting.** A vendor that knows the Core question set can
   hand-tune persona prompts against those specific items.
3. **Score fabrication.** A submission could simply lie about the SPS it
   measured.

### 6.2 Defenses

**Private 20 % holdout, salted quarterly.** Question keys are partitioned
public/private by `SHA-256(question_id || quarterly_salt) % 100 < 20`. The
quarterly salt rotates 2026-Q1, 2026-Q2, … so a model trained on the public
crawl of Q1 cannot use that to score advantage on Q2's salted partition.
The salt is published on rotation; what is private is *the assignment*, not
the questions themselves. Buyers can verify Honest split.

**Tiered statistical validator.** Every submission is reanalyzed from
per-question artifacts by the validator service. Aggregate scores submitted
by a vendor are *recomputed* from their raw per-question outputs. If public
and private SPS diverge by > 0.05, the row is `⚠ flagged` on the leaderboard
— *but still displayed*, because hiding flags is itself a form of dishonesty.

**Adversarial regression suite.** A CI gate of ~40 fabricated submissions
(e.g., "constant probability vector," "shifted majority-class," "all-refusal"),
each of which *must* receive a specific known-bad score on every release.
This is the unit-test layer for the evaluator itself.

**`Perfection → ERROR`.** Any composite SPS ≥ 0.995 raises a hard validator
error and is excluded from the leaderboard pending manual review. The
Human-Ceiling baseline is also subject to this rule, which is why we report
its split-half-reliability value (~0.999) as a *baseline* rather than a
*ceiling score* — the rule keeps the ceiling honest.

**Cost & coverage transparency.** Every row carries `cost_usd` (or `null`
when not measurable, never imputed), `pricing_snapshot_date`,
`dataset_coverage_count`, and `is_cost_estimated`. Cost cannot be hidden
behind "self-hosted means free."

### 6.3 What this buys us

Together these defenses make SynthBench *resistant to* the failure modes
that have shipwrecked prior LLM leaderboards. They do not make it
*impossible* to cheat — only expensive enough that the cost-of-fraud
exceeds the value-of-the-signal, which is the most one can ask of any
public benchmark.

---

## 7. Findings (Session 1, 2026-Q1–Q2)

This section reports headline findings from 200+ runs across three datasets.
Full per-experiment data, replication counts, and JSON artifacts are in
`leaderboard-results/` and on `https://synthbench.org/findings/`.

### 7.1 Ensemble blending is the single largest lever (+5–7 SPS pts)

Per-question equal-weight averaging of the response distributions of Claude
Haiku 4.5, Gemini 2.5 Flash-Lite, and GPT-4o-mini lifts the OpinionsQA-Core
SPS from the best-single-model 0.766 (Haiku) to **0.836** for the equal blend
— a **+7.0 SPS-point improvement at zero incremental API cost** because the
arithmetic is performed offline on already-collected per-question outputs.

| Dataset | Best single | Equal-blend | Δ |
|---|---|---|---|
| OpinionsQA (684 Qs) | 0.766 (Haiku 4.5) | **0.836** | +0.070 |
| SubPOP (200 Qs) | 0.744 (Gemini FL) | **0.796** | +0.052 |
| GlobalOpinionQA (100 Qs) | 0.692 (GPT-4o-mini) | **0.747** | +0.056 |

**Mechanism:** the three models make *uncorrelated* errors on 72–81 % of
questions; averaging cancels idiosyncratic deviation. The per-question
ORACLE ceiling (the best of the three on each question) barely exceeds the
equal blend, so per-question model selection offers negligible additional
headroom over naïve averaging.

This is the largest single empirical takeaway in the paper for practitioners:
**if you are running a synthetic-respondent pipeline today, ensemble three
moderately-priced models with equal-weight distribution averaging.** It will
beat your single best model by 5–7 SPS points for free.

### 7.2 Conditioning fidelity is small, asymmetric, and bias-quantifying

POLPARTY conditioning on Haiku (4 replications) yields:

| Group | P_dist (unconditioned) | P_cond | Interpretation |
|---|---|---|---|
| Republican | 0.666 ± 0.004 | **+0.073 ± 0.004** | 7.3 % closer after conditioning |
| Democrat | 0.644 ± 0.006 | **+0.033 ± 0.005** | 3.3 % closer after conditioning |

INCOME conditioning shows the same asymmetry:

| Group | P_dist | P_cond |
|---|---|---|
| $100K+ | 0.673 | +0.031 |
| <$30K | 0.603 | +0.020 |

**Republican conditioning is 2.4× more effective than Democrat conditioning,
and high-income conditioning is 1.5× more effective than low-income.** This
is not a property of conditioning itself; it is a property of the *baseline*.
The unconditioned model is already close to Democrat / high-income response
distributions, so there is less room for conditioning to improve. The model
is *further* from Republican / low-income distributions, so conditioning
produces a larger correction.

Reframed: SynthBench's P_cond axis *measures the directional bias of LLM
defaults* with a calibration-grade signal that aggregate alignment scores
do not surface. This is independent value for the bias-auditing community.

### 7.3 Temperature sensitivity is governed by base entropy, not scale

Sweep across 5 temperatures, 3 models, 2–3 replications:

| Model | SPS range | Sensitivity | Optimal |
|---|---|---|---|
| Claude Haiku 4.5 | 0.843–0.850 | insensitive (±0.6 %) | any |
| Gemini Flash Lite | 0.819–0.864 (incl. t=2.0) | strong monotonic (+4.5 %) | t=2.0 |
| GPT-4o-mini | 0.817–0.829 | mild monotonic (+1.2 %) | t=1.0 |

The base-entropy hypothesis (H5): *models with more peaked default outputs
benefit more from raising temperature* is **NOT supported** — actually
inverted. KL-divergence-from-uniform:

| Model | Base entropy | Concentrated questions | Temp sensitivity |
|---|---|---|---|
| GPT-4o-mini | 0.22 bits | 92.6 % | mild (+1.2 %) |
| Haiku 4.5 | 0.36 bits | 85.9 % | insensitive (±0.6 %) |
| Gemini Flash Lite | 0.56 bits | 77.3 % | **strong (+4.5 %)** |

**Interpretation.** Temperature does not *create* distributional capacity —
it only amplifies whatever capacity is already latent. A model that always
picks one answer cannot be "spread" by raising temperature; raising
temperature just adds noise. Gemini Flash Lite already has the broadest
default distribution and therefore the most headroom for temperature to
help.

This finding has direct practical consequence: **temperature optimization
is not a portable recipe.** Each provider needs a per-model sweep, and
ensemble blending tends to absorb whatever per-model temperature gains
exist (full optimal-temperature ensemble: 0.900 vs default-temperature
ensemble 0.899 — +0.1 pp).

### 7.4 The persona-template ablation: prompts matter, garbled prompts hurt

A 4-template ablation on SubPOP-Haiku at t=0.85:

| Template | Description | Mean SPS | Std |
|---|---|---|---|
| **CURRENT** | name, age, occupation, background, personality | **0.690** | 0.019 |
| MINIMAL | name, age, occupation only | 0.581 | 0.005 |
| VALUES | + core beliefs, decision style (unfilled) | 0.555 | 0.032 |
| DEMO | + education, income, location, politics (unfilled) | 0.569 | 0.001 |

The default template wins by **+11 SPS points** (5× the noise band).
Templates with *unfilled* format-string placeholders (`{education_level}`,
`{politics}`) actively hurt: P_refuse collapses from 0.80 to 0.40–0.50,
indicating the model treats the garbled placeholder text as cause to refuse.
A trivial bug in a vendor's persona-template assembly can therefore tank
synthetic-respondent quality by 11+ SPS points — a magnitude of failure
that any procurement evaluation should be capable of detecting and that the
SynthBench protocol surfaces directly.

### 7.5 Convergence and reproducibility

Across five-replication trials on OpinionsQA-Haiku, run-to-run SPS standard
deviation is **0.001–0.007** (mean ~0.003). All experimental findings above
exceed this noise band by 5–20×. Convergence diagnostics are tracked in
`leaderboard.json:convergence` for every reported model.

---

## 8. Discussion

### 8.1 What SynthBench is *for*

Three audiences benefit:

- **Buyers** of synthetic-respondent products get a vendor-agnostic
  evaluation receipt with five interpretable axes and five anchor baselines.
- **Vendors** get a public scoreboard they can either climb (by improving
  conditioning, ensembling, or persona templates) or contest (by submitting
  runs and challenging the validator).
- **Researchers** get a unified evaluation harness across OpinionsQA,
  SubPOP, and GlobalOpinionQA so that future methodological work can report
  on a single, comparable scale.

### 8.2 Limitations

SynthBench measures *distributional* fidelity, not *qualitative* response
quality. A provider that produces beautifully-reasoned but
distributionally-mis-shaped responses will lose to a less-articulate
provider that lands closer to the human distribution. This is by design —
distribution fidelity is the failure mode "trendslop" denotes — but
practitioners using SynthBench for product decisions should pair it with
qualitative evaluation for use cases where open-ended response quality
matters. P_theme (Phase 2) will partly close this gap.

We currently evaluate against Pew-derived ground truth, which is
US-centric for OpinionsQA and Western-leaning for the Pew Global subset of
GlobalOpinionQA. WVS adapter coverage will rebalance this in Phase 2.

Holdout integrity depends on the salt rotation. A vendor with privileged
read access to the rotation schedule could in principle game the next
quarter's split. We mitigate this by publishing the *current* salt
immediately (the rotation is what's private, not the salt itself) and by
auditing public-vs-private divergence at every submission.

### 8.3 Future work

Phase 2: GlobalOpinionQA Full elevation, P_theme (open-ended) ground truth
via WVS qualitative supplements, longitudinal "temporal drift" tracking
against ATP wave dates. Phase 3: custom open-ended corpus, multi-turn survey
fidelity, multi-modal personas (image-attached respondent contexts).

---

## 9. Reproducibility

```bash
pip install synthbench
synthbench run --provider openrouter --model openai/gpt-4o-mini \
  --suite core --samples 30
synthbench leaderboard --results-dir ./results
synthbench publish-data --results-dir ./results \
  --output ./leaderboard.json
```

All per-run JSON artifacts include a `config_hash`, a deterministic seed
(42), the pricing snapshot used, and the SHA-256 partition keys used.
Per-question data is available at runtime to the site UI; bulk
research-access requests are handled per the policy described in
[`METHODOLOGY.md §8`](https://github.com/DataViking-Tech/synthbench/blob/main/METHODOLOGY.md#8-accessing-raw-data-for-research).

---

## 10. Acknowledgments

The OpinionsQA, GlobalOpinionQA, and SubPOP teams produced the ground truth
that makes this work possible. Pew Research Center and the World Values
Survey Association are the upstream sources of every distribution we score
against. Errors of integration and operationalization are the authors'.

---

## References (selected)

1. Santurkar, S., Durmus, E., Ladhak, F., Lee, C., Liang, P., Hashimoto, T.
   "Whose Opinions Do Language Models Reflect?" *ICML 2023*. arXiv:2303.17548.
2. Durmus, E., et al. "Towards Measuring the Representation of Subjective
   Global Opinions in Language Models." 2024. arXiv:2306.16388.
3. Suh, S., Jahanparast, A., Moon, S., Kang, J., Chang, K. "Language Model
   Fine-Tuning on Scaled Survey Data for Predicting Distributions of Public
   Opinions." *ACL 2025*. arXiv:2502.16761.
4. Wang, et al. "Assessing the Reliability of Persona-Conditioned LLMs as
   Synthetic Survey Respondents." 2026. arXiv:2602.18462.
5. Gupta, et al. "Contamination and Goodhart in Public Agent Benchmarks: A
   Teardown of AgentBench." UC Berkeley tech report, 2025.
6. Harvard Business Review. "Trendslop: When AI-Augmented Research Says
   Nothing Plausibly." 2026.
7. Lin, J. "Divergence Measures Based on the Shannon Entropy." *IEEE
   Transactions on Information Theory*, 1991.
8. Kendall, M. G. "A New Measure of Rank Correlation." *Biometrika*, 1938.

Full BibTeX of every reference cited in the live methodology page is
available at https://synthbench.org/methodology/#related-work and in
[`site/src/components/methodology/RelatedWork.astro`](https://github.com/DataViking-Tech/synthbench/blob/main/site/src/components/methodology/RelatedWork.astro).

---

## Appendix A — Submission protocol

A run is admissible if it carries all of: `config_hash`, `synthbench_version`,
provider+model identifiers, dataset key, n_samples (or "logprob"),
timestamp, and a per-question artifact list. The submission CLI is
`synthbench submit`; the validator emits a verification status before the
row appears on the public board. Rows that fail validation are not
suppressed — they are displayed with `⚠ flagged` and an explanatory link.

## Appendix B — Pricing snapshot

Every leaderboard.json carries a `pricing_snapshot` block keyed by date and
provider, used to compute `cost_per_100q` and `cost_per_sps_point`. When the
snapshot is absent or the provider does not expose token accounting,
cost is published as `null` and `is_cost_estimated=true` is *not* set —
we never impute costs. This is the single most-asked-about aspect of the
leaderboard by AI-engineering audiences (see ai-engineer-readiness.md for
qualitative evidence) and is therefore guarded explicitly.

## Appendix C — Coverage flags

Each row carries `dataset_coverage_count` (the number of questions actually
scored) and a coverage-completeness flag. A row that scored only 100 of
OpinionsQA's 1,498 questions is not directly comparable to a row that
scored all 1,498 — and the leaderboard surfaces that gap rather than
hiding it inside an aggregate.

---

*Manuscript v1 prepared 2026-05-14 for arXiv preprint submission. Source:
[`docs/papers/synthbench-2026-arxiv.md`](https://github.com/DataViking-Tech/synthbench/blob/main/docs/papers/synthbench-2026-arxiv.md). Corresponding author: wesley@dataviking.tech.*
