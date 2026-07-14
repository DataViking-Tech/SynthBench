# SynthBench Research Findings

**Date**: 2026-04-12 (session-1 experiments) | **Numbers regenerated from artifacts** — see below

> All quantitative tables in this document sit between
> `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->` markers and are
> rendered by `scripts/generate-findings-md.py` from the per-question rows
> committed in `leaderboard-results/`, using the same recompute path that
> ranks the leaderboard (#305). CI fails if these sections drift from the
> artifacts (`tests/test_findings_drift.py`). Hand-written prose lives
> outside the markers; numbers that cannot be derived from committed
> artifacts are listed in the [Asserted constants](#asserted-constants)
> appendix.

---

## Executive Summary

Six experiments across 3 models, 3 datasets, and 200+ benchmark runs reveal
that **multi-model ensemble blending is the single largest lever for
improving synthetic survey quality**, while temperature tuning and
demographic conditioning provide smaller, model-specific gains. The
benchmark also functions as a bias auditing tool, quantifying systematic
asymmetries in how LLMs represent different demographic groups.

<!-- BEGIN GENERATED: headline -->
**Metric convention**: all SPS values below use the `sps` composite (equal-weighted mean of all available components), recomputed from per-question rows at publish time (#305). Random baselines score 0.710/0.763/0.757 on this scale (globalopinionqa, opinionsqa, subpop) — read every headline against that floor, not against 0.

| Dataset | 3-model ensemble SPS | Best single model | Random baseline |
|---------|---------------------|-------------------|-----------------|
| globalopinionqa (n=100) | **0.813** | 0.786 (SynthPanel (GPT-4o-mini), product) | 0.710 (n=10) |
| opinionsqa (n=684) | **0.877** | 0.829 (Gemini 2.5 Flash, raw) | 0.763 (n=684) |
| subpop (n=200) | **0.831** | 0.821 (SynthPanel (Gemini Flash Lite), product) | 0.757 (n=200) |
<!-- END GENERATED: headline -->

Note on interpretation: SPS is a composite parity score, not a
"percent indistinguishable". An earlier version of this document described
the ensemble's OpinionsQA score as "SPS 0.900 — 90% indistinguishable from
real human survey data"; that reading overstated the metric and was computed
under the retired 2-metric composite. The scores above are the current
full-composite values with their baseline floors alongside.

---

## Experiment A: Temperature Sensitivity

**Question**: Does sampling temperature affect how well models reproduce human survey distributions?

**Method**: 5 temperatures (0.3, 0.5, 0.7, 0.85, 1.0) × 3 models × 2–3
replications each, on OpinionsQA (100 questions, 30 samples/question);
Gemini Flash Lite extended to t=2.0 (Experiment D).

### Results

<!-- BEGIN GENERATED: temperature -->
| Model | Temp range | SPS range (mean) | Δ (pts) | Replications/cell |
|-------|-----------|------------------|---------|-------------------|
| Claude Haiku 4.5 | 0.3–1.0 | 0.843–0.850 | +0.8 | 3 |
| GPT-4o-mini | 0.3–1.0 | 0.817–0.829 | +1.2 | 2 |
| Gemini Flash Lite | 0.3–2.0 | 0.819–0.864 | +4.5 | 2 |

Full sweep (mean ± std across replications):

| Model | Temp | SPS | n |
|-------|------|-----|---|
| Claude Haiku 4.5 | 0.3 | 0.843 ± 0.003 | 3 |
| Claude Haiku 4.5 | 0.5 | 0.844 ± 0.003 | 3 |
| Claude Haiku 4.5 | 0.7 | 0.845 ± 0.007 | 3 |
| Claude Haiku 4.5 | 0.85 | 0.850 ± 0.006 | 3 |
| Claude Haiku 4.5 | 1.0 | 0.844 ± 0.007 | 3 |
| GPT-4o-mini | 0.3 | 0.817 ± 0.000 | 2 |
| GPT-4o-mini | 0.5 | 0.822 ± 0.001 | 2 |
| GPT-4o-mini | 0.7 | 0.822 ± 0.000 | 2 |
| GPT-4o-mini | 0.85 | 0.824 ± 0.002 | 2 |
| GPT-4o-mini | 1.0 | 0.829 ± 0.001 | 2 |
| Gemini Flash Lite | 0.3 | 0.819 ± 0.003 | 2 |
| Gemini Flash Lite | 0.5 | 0.827 ± 0.001 | 2 |
| Gemini Flash Lite | 0.7 | 0.838 ± 0.005 | 2 |
| Gemini Flash Lite | 0.85 | 0.849 ± 0.003 | 2 |
| Gemini Flash Lite | 1.0 | 0.856 ± 0.003 | 2 |
| Gemini Flash Lite | 1.2 | 0.856 ± 0.001 | 2 |
| Gemini Flash Lite | 1.5 | 0.858 ± 0.000 | 2 |
| Gemini Flash Lite | 1.8 | 0.857 ± 0.005 | 2 |
| Gemini Flash Lite | 2.0 | 0.864 ± 0.001 | 2 |
<!-- END GENERATED: temperature -->

### Key Finding

Temperature sensitivity is **model-specific**, not universal. Gemini Flash
Lite shows a strong monotonic gain; GPT-4o-mini a mild one; Claude Haiku 4.5
moves within its own noise band (its per-cell std overlaps the spread, and
its t=0.85 mean edges out t=1.0). The effect correlates with base output
entropy (see Experiment H5 below).

---

## Experiment B: Persona Template Variants

**Question**: Does the structure of the persona system prompt affect survey quality?

**Method**: 4 template variants × 2 replications on SubPOP (100 questions,
30 samples), all at t=0.85 with Haiku.

<!-- BEGIN GENERATED: template -->
| Template | Mean SPS | Std | Runs |
|----------|----------|-----|------|
| **CURRENT** | **0.690** | 0.019 | 2 |
| MINIMAL | 0.581 | 0.005 | 2 |
| DEMO | 0.569 | 0.001 | 2 |
| VALUES | 0.555 | 0.032 | 2 |

The CURRENT template beats the best alternative by **+11.0 SPS points**.
<!-- END GENERATED: template -->

### Key Finding

The default (CURRENT) template wins decisively — well outside the noise
band. Templates with unfilled format-string placeholders
(`{education_level}`) actively hurt; the session-1 analysis attributed this
to refusal collapse (see asserted constants).

---

## Experiment B v2: Demographic Conditioning

**Question**: Does telling the model "you are a Republican" actually shift its responses toward real Republican survey data?

**Method**: Per-group conditioned evaluation on SubPOP using POLPARTY,
INCOME, EDUCATION, RACE, RELIG, CREGION, and SEX attributes. Haiku at
t=0.85, 100 questions, 15–30 samples.

<!-- BEGIN GENERATED: conditioning -->
#### POLPARTY

| Group | P_dist | P_cond | Replications |
|-------|--------|--------|--------------|
| Republican | 0.666 | **0.073 ± 0.004** | 4 |
| Democrat | 0.644 | **0.033 ± 0.005** | 4 |

#### INCOME

| Group | P_dist | P_cond | Replications |
|-------|--------|--------|--------------|
| $100K+ | 0.674 | **0.030 ± 0.004** | 3 |
| <$30K | 0.596 | **0.019 ± 0.003** | 3 |

#### EDUCATION

| Group | P_dist | P_cond | Replications |
|-------|--------|--------|--------------|
| Less than HS | 0.597 | **0.038** | 1 |
| College graduate | 0.641 | **0.036** | 1 |

Republican conditioning is **2.2× stronger** than Democrat (mean P_cond across replications).
High-income conditioning is **1.5× stronger** than low-income.

#### Other measured attributes

| Attribute | Group | P_dist | P_cond | Replications |
|-----------|-------|--------|--------|--------------|
| CREGION | South | 0.641 | 0.039 ± 0.005 | 2 |
| CREGION | Northeast | 0.628 | 0.021 ± 0.004 | 2 |
| RACE | White | 0.785 | 0.141 ± 0.030 | 3 |
| RACE | Hispanic | 0.605 | 0.034 ± 0.005 | 3 |
| RACE | Asian | 0.637 | 0.025 ± 0.005 | 3 |
| RACE | Black | 0.585 | 0.025 ± 0.003 | 3 |
| RELIG | Protestant | 0.838 | 0.178 | 1 |
| RELIG | Muslim | 0.820 | 0.161 | 1 |
| RELIG | Hindu | 0.806 | 0.129 | 1 |
| RELIG | Jewish | 0.774 | 0.127 | 1 |
| RELIG | Atheist | 0.738 | 0.095 | 1 |
| SEX | Male | 0.647 | 0.055 | 1 |
| SEX | Female | 0.617 | 0.027 | 1 |
<!-- END GENERATED: conditioning -->

### Key Findings

1. **Conditioning works but the effect is small** (roughly 2–7% improvement
   per group on the core political/income/education attributes).
2. **Republican conditioning is stronger than Democrat** (ratio in the
   generated section above — the model's unconditioned output already
   approximates Democrat response patterns). This quantifies the documented
   progressive lean in LLM defaults. An earlier version of this document
   reported this ratio as 2.4×; the artifact-derived value is 2.2×.
3. **High-income conditioning is stronger than low-income** — the model is
   systematically worse at reproducing low-income response distributions
   (P_dist gap visible in the table).
4. **These asymmetries are publishable calibration findings.** The benchmark
   functions as a bias auditing tool, not just an accuracy leaderboard.

---

## Experiment C: Ensemble Blending

**Question**: Does averaging response distributions across multiple models beat any single model?

**Method**: Per-question distribution blending of Haiku + Gemini Flash Lite
+ GPT-4o-mini results. The blend itself is pure arithmetic on existing data —
no new model calls beyond the three constituent runs — but producing all
three runs costs roughly 3× a single-model run.

### Results

<!-- BEGIN GENERATED: ensemble -->
| Dataset | Best single model | Equal blend | Improvement | Random baseline |
|---------|-------------------|-------------|-------------|-----------------|
| globalopinionqa (100q) | 0.786 (SynthPanel (GPT-4o-mini), product) | **0.813** | **+2.7 pts** | 0.710 (n=10) |
| opinionsqa (684q) | 0.829 (Gemini 2.5 Flash, raw) | **0.877** | **+4.8 pts** | 0.763 (n=684) |
| subpop (200q) | 0.821 (SynthPanel (Gemini Flash Lite), product) | **0.831** | **+1.0 pts** | 0.757 (n=200) |

Comparison set: best_single = highest recomputed-SPS non-ensemble, non-baseline leaderboard row (raw or product framework) evaluated on at least as many questions as the ensemble, after per-(model, framework, dataset) dedup; random_baseline = recomputed SPS of the random-baseline run for the same dataset (n in random_baseline_n).
<!-- END GENERATED: ensemble -->

### Key Findings

1. **Largest single lever discovered.** The size of the gain depends on the
   comparison set: against the best single leaderboard entry at matched
   question count it ranges per dataset as shown above. (An earlier version
   of this document claimed "+5–7 pts consistent across all 3 datasets";
   that figure came from comparing only against the three blend
   constituents under the retired composite convention.)
2. **Simple equal-weight averaging is optimal** — score-proportional and
   inverse-JSD weighting produce near-identical results (asserted constant).
3. Most individual questions improve under blending; models make
   uncorrelated errors on different questions (asserted constant).
4. **ORACLE ceiling barely exceeds equal blend** — per-question model
   selection offers negligible headroom over naive averaging (asserted
   constant).

### Optimal-Temperature Ensemble (Experiment E) — superseded

An earlier version of this section reported a "SPS 0.900" optimal-temperature
ensemble on OpinionsQA. Those numbers were computed under the retired
2-metric composite from blend files that were never committed to
`leaderboard-results/`, and are **superseded** by the recomputed
default-temperature ensemble scores in the table above. Re-running the
optimal-temperature blend under the current convention is open follow-up
work.

---

## Experiment D: Gemini Extended Temperature

**Question**: Does Gemini Flash Lite's monotonic improvement continue past t=1.0?

**Method**: t={1.2, 1.5, 1.8, 2.0} × 2 replications on OpinionsQA.

<!-- BEGIN GENERATED: extended-temperature -->
| Temp | Mean SPS | n |
|------|----------|---|
| 1.0 | 0.856 ± 0.003 | 2 |
| 1.2 | 0.856 ± 0.001 | 2 |
| 1.5 | 0.858 ± 0.000 | 2 |
| 1.8 | 0.857 ± 0.005 | 2 |
| **2.0** | **0.864 ± 0.001** | 2 |
<!-- END GENERATED: extended-temperature -->

### Key Finding

**No peak found even at t=2.0.** Gemini's base output entropy is low enough
that extreme temperatures still improve distributional matching. The plateau
from 1.0–1.8 then jump at 2.0 may reflect discrete regime changes in the
inference backend.

---

## Experiment H5: Base Entropy Predicts Temperature Sensitivity

**Question**: Do models with more concentrated (peaked) default outputs benefit more from raising temperature?

**Method**: Compute KL divergence from uniform for each model's
default-temperature outputs (session-1 notebook analysis; entropy values are
asserted constants — see appendix).

### Key Finding

**Hypothesis NOT supported — actually inverted.** The model with the highest
base entropy (Gemini, already most diverse) benefits most from temperature.
The most peaked model (GPT-4o-mini) shows minimal improvement.

**Interpretation**: Temperature amplifies existing distributional capacity;
it doesn't create it. A model hardcoded to pick one answer won't spread with
more temperature — it just adds noise.

---

## Lever Hierarchy

<!-- BEGIN GENERATED: levers -->
| Lever | Effect size (SPS pts) | Cost | Status |
|-------|----------------------|------|--------|
| **Ensemble blending** | +1.0–4.8 | zero | done |
| **Per-model optimal temperature** | +0.8–4.5 | low | actionable |
| **Demographic conditioning** | +1.9–7.3 | moderate | scientific |
| **Persona template** | 'current' template already optimal (+11.0 pts over the best alternative); no further gain available from this lever. | zero | done |
<!-- END GENERATED: levers -->

---

## Asserted constants

<!-- BEGIN GENERATED: asserted-constants -->
The following claims are **not derivable from the committed artifacts** and are carried as asserted constants (also published in the findings block's `asserted_constants` list, which the CI drift guard checks):

| Claim | Source |
|-------|--------|
| equal-weight ~= score-proportional ~= inverse-JSD (to 3 decimals) | Session-1 ensemble weighting comparison (2026-04-12); the alternative-weighting blend files were not committed to leaderboard-results/, so this is not reproducible from artifacts. |
| 72-81% of individual questions improve under blending | Session-1 per-question blend analysis (2026-04-12), computed under the retired parity-2 convention; not recomputed since. |
| per-question oracle model selection barely exceeds the equal blend | Session-1 oracle analysis (2026-04-12); oracle blend files were not committed to leaderboard-results/. |
| base output entropy (bits, default temperature): GPT-4o-mini 0.22, Claude Haiku 4.5 0.36, Gemini Flash Lite 0.56 | Experiment H5 notebook analysis (2026-04-12) of default-temperature model_distribution rows; the notebook output was not committed, so the exact values are asserted. |
| P_refuse collapses from ~0.80 to 0.40-0.50 on templates with unfilled format-string placeholders | Session-1 template-variant analysis (2026-04-12); per-component P_refuse for the template runs is derivable in principle but the published block only tracks composite SPS for templates. |
<!-- END GENERATED: asserted-constants -->

---

## Datasets

All experiments use publicly available survey datasets with real human response distributions:

| Dataset | Questions | Demographics | Source |
|---------|-----------|-------------|--------|
| OpinionsQA | 684 | US population | Pew Research ATP surveys |
| SubPOP | 3,362 | 22 US subpopulations | Suh et al., ACL 2025 |
| GlobalOpinionQA | 2,556 | Cross-country | Pew Global Attitudes |

---

## Reproducibility

- All result JSON files are stored in `leaderboard-results/`
- Each file contains per-question distributions, metadata, and configuration
- The `synthbench ensemble` CLI command reproduces blending results from saved files
- Generated sections of this document: `python scripts/generate-findings-md.py`
  (CI-checked against the artifacts by `tests/test_findings_drift.py`)
- Run-to-run standard deviations reported for all replicated experiments
