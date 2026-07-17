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

**Scope of claim**: every score in this document measures distributional
fidelity to specific surveys (Pew ATP via OpinionsQA, SubPOP,
GlobalOpinionQA, GSS) — not validity of synthetic respondents, accuracy of
individual responses, or real-world behavior prediction. See
[What SPS does — and does not — measure](https://synthbench.org/methodology/#scope-of-claim).

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
| subpop (n=200) | **0.858** | 0.821 (SynthPanel (Gemini Flash Lite), product) | 0.757 (n=200) |
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

## Experiment B v3: Elicitation Mode (Natural vs Schema-Forced)

**Question**: Does forcing panelists to answer through a structured response
schema (guaranteed-parseable capture) cost anything relative to natural
in-character roleplay elicitation?

**Method**: One matched pair on GSS (75 questions, 30 samples per question,
refusal detector v2): the SynthPanel Haiku 4.5 default (natural roleplay)
run vs the identical configuration with schema-forced structured capture
(`tpl=structured`, #328). Same model, dataset, question set, and sample
count — the elicitation surface is the only variable.

<!-- BEGIN GENERATED: elicitation -->
**SynthPanel (Haiku 4.5)** (product) on gss — n=75 questions × 30 samples per arm, refusal detector v2; the arms differ only in elicitation mode:

| Metric | Natural | Structured | Δ (structured − natural) |
|--------|---------|------------|--------------------------|
| SPS | 0.803 | 0.791 | **-1.2 pts** |
| P_dist | 0.714 | 0.666 | **-4.7 pts** |
| P_rank | 0.724 | 0.736 | **+1.2 pts** |
| P_refuse | 0.972 | 0.972 | **+0.0 pts** |
| Parse failures | 1.6% | 0.0% | -1.6 pts |

Comparison set: Matched pairs of deduped runs differing only in elicitation mode: a run whose config carries an explicit elicitation template variant (e.g. tpl=structured, schema-forced capture) vs the natural-elicitation run of the identical configuration (same base provider, dataset, samples_per_question, question_set_hash, temperature, effort, and question count). All scores recomputed from per-question rows; deltas are structured minus natural.
<!-- END GENERATED: elicitation -->

### Key Finding

Schema-forced capture eliminates parse failures entirely, but measurably
lowers distributional fidelity: natural in-character elicitation appears to
be load-bearing for human-likeness, and the parsing win does not pay for
the P_dist loss at the composite level. Elicitation mode is now a labeled
template variant on the leaderboard, so the two surfaces stay separately
ranked.

**Caveat**: this is a single model × single dataset × one matched pair — a
suggestive first datapoint, not a general law. More pairs (other models,
other datasets, replications) are needed before treating the fidelity cost
as systematic.

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
| Republican | 0.680 | **0.099 ± 0.035** | 9 |
| Democrat | 0.657 | **0.043 ± 0.023** | 9 |

#### INCOME

| Group | P_dist | P_cond | Replications |
|-------|--------|--------|--------------|
| <$30K | 0.632 | **0.054 ± 0.033** | 8 |
| $100K+ | 0.673 | **0.041 ± 0.025** | 8 |

#### EDUCATION

| Group | P_dist | P_cond | Replications |
|-------|--------|--------|--------------|
| Less than HS | 0.642 | **0.081 ± 0.041** | 6 |
| College graduate | 0.676 | **0.042 ± 0.026** | 6 |

Republican conditioning is **2.3× stronger** than Democrat (mean P_cond across replications).
High-income conditioning is **1.3× stronger** than low-income.

#### Other measured attributes

| Attribute | Group | P_dist | P_cond | Replications |
|-----------|-------|--------|--------|--------------|
| CREGION | South | 0.651 | 0.055 ± 0.018 | 7 |
| CREGION | Northeast | 0.657 | 0.045 ± 0.029 | 7 |
| RACE | White | 0.785 | 0.141 ± 0.030 | 3 |
| RACE | Hispanic | 0.605 | 0.034 ± 0.005 | 3 |
| RACE | Asian | 0.637 | 0.025 ± 0.005 | 3 |
| RACE | Black | 0.585 | 0.025 ± 0.003 | 3 |
| RELIG | Protestant | 0.838 | 0.178 | 1 |
| RELIG | Muslim | 0.820 | 0.161 | 1 |
| RELIG | Hindu | 0.806 | 0.129 | 1 |
| RELIG | Jewish | 0.774 | 0.127 | 1 |
| RELIG | Atheist | 0.738 | 0.095 | 1 |
| SEX | Female | 0.645 | 0.049 ± 0.036 | 6 |
| SEX | Male | 0.665 | 0.048 ± 0.031 | 6 |
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
| subpop (200q) | 0.821 (SynthPanel (Gemini Flash Lite), product) | **0.858** | **+3.7 pts** | 0.757 (n=200) |

Comparison set: best_single = highest recomputed-SPS non-ensemble, non-baseline leaderboard row (raw or product framework) evaluated on at least as many questions as the ensemble, after per-(model, framework, dataset) dedup; random_baseline = recomputed SPS of the random-baseline run for the same dataset (n in random_baseline_n).
<!-- END GENERATED: ensemble -->

### Error correlation between constituents

**Question**: The ensemble was originally framed as working because the
constituents make "uncorrelated errors". Is that true?

**Method**: For each dataset's published ensemble, pairwise Pearson r
between the constituent runs' committed per-question JSD-vs-human vectors
over the ensemble's common question set (do the constituents err on the
same questions?), plus signed per-option residual correlations computed
against the canonical human distributions (do the errors point the same
way?) — the latter carried as an asserted constant because committed gated
artifacts strip `human_distribution` (#308).

<!-- BEGIN GENERATED: ensemble-error-correlation -->
**globalopinionqa** (n=100 common questions, mean pairwise r = 0.407):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| SynthPanel (Haiku 4.5) ↔ SynthPanel (Gemini Flash Lite) | 0.419 | 100 |
| SynthPanel (Haiku 4.5) ↔ SynthPanel (GPT-4o-mini) | 0.308 | 100 |
| SynthPanel (Gemini Flash Lite) ↔ SynthPanel (GPT-4o-mini) | 0.493 | 100 |

**opinionsqa** (n=684 common questions, mean pairwise r = 0.295):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| SynthPanel (Haiku 4.5) ↔ SynthPanel (Gemini Flash Lite) | 0.224 | 684 |
| SynthPanel (Haiku 4.5) ↔ SynthPanel (GPT-4o-mini) | 0.355 | 684 |
| SynthPanel (Gemini Flash Lite) ↔ SynthPanel (GPT-4o-mini) | 0.308 | 684 |

**subpop** (n=200 common questions, mean pairwise r = 0.322):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| SynthPanel (Haiku 4.5) ↔ SynthPanel (Gemini Flash Lite) | 0.282 | 200 |
| SynthPanel (Haiku 4.5) ↔ SynthPanel (GPT-4o-mini) | 0.260 | 200 |
| SynthPanel (Gemini Flash Lite) ↔ SynthPanel (GPT-4o-mini) | 0.425 | 200 |

The constituents' errors are **moderately positively correlated** (pairwise r 0.22–0.49 on per-question JSD; 0.27–0.44 on signed per-option residuals, see asserted constants) — not uncorrelated. The ensemble gain comes from partial, not full, independence of errors; the earlier "uncorrelated errors" framing overstated it.

Comparison set: For each dataset's published ensemble: pairwise Pearson r between the constituent runs' committed per-question JSD vectors (each run's error magnitude vs the canonical human distribution), over the ensemble's common question set, read from the exact files named in ensemble_sources. Measures whether constituents err on the same questions. Signed per-option residual correlations need the stripped human_distribution fields (#308) and are carried as the ensemble_signed_error_correlation asserted constant.
<!-- END GENERATED: ensemble-error-correlation -->

### Key Findings

1. **Largest single lever discovered.** The size of the gain depends on the
   comparison set: against the best single leaderboard entry at matched
   question count it ranges per dataset as shown above. (An earlier version
   of this document claimed "+5–7 pts consistent across all 3 datasets";
   that figure came from comparing only against the three blend
   constituents under the retired composite convention.)
2. **Simple equal-weight averaging is optimal** — score-proportional and
   inverse-JSD weighting produce near-identical results (asserted constant).
3. Most individual questions improve under blending (asserted constant),
   but the constituents' errors are **moderately positively correlated**
   (pairwise r ≈ 0.22–0.49 on per-question JSD, 0.27–0.44 on signed
   per-option residuals — see the error-correlation matrix above). The
   gain comes from partial, not full, independence; the earlier
   "uncorrelated errors" framing overstated it.
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
| **Ensemble blending** | +2.7–4.8 | zero | done |
| **Per-model optimal temperature** | +0.8–4.5 | low | actionable |
| **Demographic conditioning** | +4.1–9.9 | moderate | scientific |
| **Persona template** | 'current' template already optimal (+11.0 pts over the best alternative); no further gain available from this lever. | zero | done |
<!-- END GENERATED: levers -->

---

## Nonresponse Fidelity

How closely does each model's explicit-nonresponse mass ("don't know"-style
option selections plus parsed refusals) track the human survey's? Computed
per run from the committed per-question rows (full-tier datasets only —
gated files are committed without `human_distribution`).

<!-- BEGIN GENERATED: nonresponse-fidelity -->
| Provider | Framework | Template | Dataset | Mean model nonresponse | Mean human nonresponse | Mean abs gap | n |
|----------|-----------|----------|---------|------------------------|------------------------|--------------|---|
| Gemini 2.5 Flash | raw | default | gss | 0.106 | 0.056 | **0.126** | 75 |
| SynthPanel (Haiku 4.5) | product | structured | gss | 0.064 | 0.056 | **0.095** | 75 |
| SynthPanel (Haiku 4.5) | product | default | gss | 0.067 | 0.056 | **0.094** | 75 |

Comparison set: Per deduped non-baseline run whose committed per-question rows still carry human_distribution (full-tier datasets; gated files are stripped per #308): mean |model explicit-nonresponse mass (DK-style option mass + parsed refusal rate) - human's|, plus the five items with the largest model over-selection.

**Safety-aligned models over-select explicit nonresponse options on sensitive items** (Gemini 2.5 Flash, gss, n=75): mean model nonresponse mass 0.106 vs human 0.056. Worst items:

| Item | Model nonresponse | Human nonresponse |
|------|-------------------|-------------------|
| GSS_FEPRESCH | 97% | 2.2% |
| GSS_NATRACE | 83% | 8.8% |
| GSS_POSTLIFE | 100% | 27.0% |
| GSS_NATHEAL | 70% | 2.4% |
| GSS_NATFARE | 63% | 4.6% |

Nonresponse mass concentrates on religion, gender-role, race, and welfare topics; the model selects a legitimate 'don't know'-style option rather than refusing in prose, so the sidestepping is invisible to refusal-rate metrics and only surfaces in the option distribution itself.
<!-- END GENERATED: nonresponse-fidelity -->

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
| pairwise Pearson r of constituents' per-option signed residuals (model probability − human probability) on the ensemble common question sets: globalopinionqa 0.27–0.44, opinionsqa 0.36–0.38, subpop 0.36–0.42 — all pairs moderately positively correlated | Computed 2026-07-16 from the committed constituents' per-question model_distribution rows plus canonical human-distribution rehydration (synthbench.human_distributions); committed gated artifacts strip human_distribution (#308), so the signed residuals are not derivable from public artifacts alone. The JSD-based correlations in ensemble_error_correlation ARE derivable and are recomputed by the drift guard. |
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
