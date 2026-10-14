# SynthBench Research Findings

**Date**: 2026-04-12 (session-1 experiments) | **Numbers regenerated from artifacts** — see below

> **Naming note (2026-07):** the `synthpanel` provider referenced throughout
> these findings was renamed to **[althing](https://althing.dev)**. Result
> artifacts and generated tables retain the provider id `synthpanel` they
> were recorded under; `--provider synthpanel` remains a working alias for
> the `althing` provider.

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
**Metric convention**: all SPS values below use the `sps` composite (equal-weighted mean of all available components), recomputed from per-question rows at publish time (#305). Random baselines score 0.774/0.774/0.774/0.774/0.774/0.735/0.735/0.735/0.735/0.735/0.763/0.763/0.763/0.763/0.763/0.757/0.757/0.757/0.757/0.757 on this scale (globalopinionqa, globalopinionqa, globalopinionqa, globalopinionqa, globalopinionqa, gss, gss, gss, gss, gss, opinionsqa, opinionsqa, opinionsqa, opinionsqa, opinionsqa, subpop, subpop, subpop, subpop, subpop) — read every headline against that floor, not against 0.

| Dataset | 3-model ensemble SPS | Best single model | Random baseline |
|---------|---------------------|-------------------|-----------------|
| globalopinionqa (n=100) | **0.810** | 0.799 (Althing (Qwen 3.8 Flash), product) | 0.774 (n=100) |
| globalopinionqa (n=100) | **0.831** | 0.799 (Althing (Qwen 3.8 Flash), product) | 0.774 (n=100) |
| globalopinionqa (n=100) | **0.818** | 0.799 (Althing (Qwen 3.8 Flash), product) | 0.774 (n=100) |
| globalopinionqa (n=100) | **0.825** | 0.799 (Althing (Qwen 3.8 Flash), product) | 0.774 (n=100) |
| globalopinionqa (n=100) | **0.817** | 0.799 (Althing (Qwen 3.8 Flash), product) | 0.774 (n=100) |
| gss (n=75) | **0.816** | 0.849 (Althing (Qwen 3.8 Flash), product) | 0.735 (n=75) |
| gss (n=75) | **0.863** | 0.849 (Althing (Qwen 3.8 Flash), product) | 0.735 (n=75) |
| gss (n=75) | **0.848** | 0.849 (Althing (Qwen 3.8 Flash), product) | 0.735 (n=75) |
| gss (n=75) | **0.851** | 0.849 (Althing (Qwen 3.8 Flash), product) | 0.735 (n=75) |
| gss (n=75) | **0.845** | 0.849 (Althing (Qwen 3.8 Flash), product) | 0.735 (n=75) |
| opinionsqa (n=100) | **0.871** | 0.874 (DeepSeek V4.1 Flash, raw) | 0.763 (n=684) |
| opinionsqa (n=100) | **0.913** | 0.874 (DeepSeek V4.1 Flash, raw) | 0.763 (n=684) |
| opinionsqa (n=100) | **0.897** | 0.874 (DeepSeek V4.1 Flash, raw) | 0.763 (n=684) |
| opinionsqa (n=100) | **0.906** | 0.874 (DeepSeek V4.1 Flash, raw) | 0.763 (n=684) |
| opinionsqa (n=100) | **0.891** | 0.874 (DeepSeek V4.1 Flash, raw) | 0.763 (n=684) |
| subpop (n=100) | **0.823** | 0.838 (DeepSeek V4.1 Flash, raw) | 0.757 (n=200) |
| subpop (n=100) | **0.865** | 0.838 (DeepSeek V4.1 Flash, raw) | 0.757 (n=200) |
| subpop (n=100) | **0.846** | 0.838 (DeepSeek V4.1 Flash, raw) | 0.757 (n=200) |
| subpop (n=100) | **0.856** | 0.838 (DeepSeek V4.1 Flash, raw) | 0.757 (n=200) |
| subpop (n=100) | **0.859** | 0.838 (DeepSeek V4.1 Flash, raw) | 0.757 (n=200) |
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
| Claude Haiku 4.5 | 0.3–1.0 | 0.814–0.830 | +1.6 | 1 |
| GPT-4o-mini | 0.3–1.0 | 0.792–0.807 | +1.5 | 1 |
| Gemini Flash Lite | 0.3–2.0 | 0.796–0.841 | +4.5 | 1 |

Full sweep (mean ± std across replications):

| Model | Temp | SPS | n |
|-------|------|-----|---|
| Claude Haiku 4.5 | 0.3 | 0.814 | 1 |
| Claude Haiku 4.5 | 0.5 | 0.821 | 1 |
| Claude Haiku 4.5 | 0.7 | 0.825 | 1 |
| Claude Haiku 4.5 | 0.85 | 0.826 | 1 |
| Claude Haiku 4.5 | 1.0 | 0.830 | 1 |
| GPT-4o-mini | 0.3 | 0.792 | 1 |
| GPT-4o-mini | 0.5 | 0.798 | 1 |
| GPT-4o-mini | 0.7 | 0.802 | 1 |
| GPT-4o-mini | 0.85 | 0.803 | 1 |
| GPT-4o-mini | 1.0 | 0.807 | 1 |
| Gemini Flash Lite | 0.3 | 0.796 | 1 |
| Gemini Flash Lite | 0.5 | 0.806 | 1 |
| Gemini Flash Lite | 0.7 | 0.815 | 1 |
| Gemini Flash Lite | 0.85 | 0.824 | 1 |
| Gemini Flash Lite | 1.0 | 0.830 | 1 |
| Gemini Flash Lite | 1.2 | 0.835 | 1 |
| Gemini Flash Lite | 1.5 | 0.834 | 1 |
| Gemini Flash Lite | 1.8 | 0.841 | 1 |
| Gemini Flash Lite | 2.0 | 0.841 | 1 |
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
| **CURRENT** | **0.725** | — | 1 |
| DEMO | 0.667 | — | 1 |
| MINIMAL | 0.648 | — | 1 |
| VALUES | 0.637 | — | 1 |

The CURRENT template beats the best alternative by **+5.8 SPS points**.
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
**Althing (GPT-6 Luna)** (product) on globalopinionqa — n=100 questions × 30 samples per arm, refusal detector v3; the arms differ only in elicitation mode:

| Metric | Natural | Structured | Δ (structured − natural) |
|--------|---------|------------|--------------------------|
| SPS | 0.762 | 0.765 | **+0.2 pts** |
| P_dist | 0.665 | 0.654 | **-1.1 pts** |
| P_rank | 0.642 | 0.661 | **+1.9 pts** |
| P_refuse | 0.980 | 0.980 | **+0.0 pts** |
| Parse failures | 0.8% | 0.0% | -0.8 pts |

**Althing (Haiku 5.5)** (product) on globalopinionqa — n=100 questions × 30 samples per arm, refusal detector v4; the arms differ only in elicitation mode:

| Metric | Natural | Structured | Δ (structured − natural) |
|--------|---------|------------|--------------------------|
| SPS | 0.774 | 0.753 | **-2.1 pts** |
| P_dist | 0.660 | 0.609 | **-5.1 pts** |
| P_rank | 0.684 | 0.670 | **-1.4 pts** |
| P_refuse | 0.979 | 0.980 | **+0.1 pts** |
| Parse failures | 0.7% | 0.0% | -0.6 pts |

**Althing (GPT-6 Luna)** (product) on opinionsqa — n=100 questions × 30 samples per arm, refusal detector v3; the arms differ only in elicitation mode:

| Metric | Natural | Structured | Δ (structured − natural) |
|--------|---------|------------|--------------------------|
| SPS | 0.833 | 0.816 | **-1.7 pts** |
| P_dist | 0.746 | 0.728 | **-1.8 pts** |
| P_rank | 0.758 | 0.724 | **-3.4 pts** |
| P_refuse | 0.994 | 0.994 | **+0.0 pts** |
| Parse failures | 0.5% | 0.0% | -0.5 pts |

**Althing (Haiku 5.5)** (product) on opinionsqa — n=100 questions × 30 samples per arm, refusal detector v4; the arms differ only in elicitation mode:

| Metric | Natural | Structured | Δ (structured − natural) |
|--------|---------|------------|--------------------------|
| SPS | 0.823 | 0.834 | **+1.2 pts** |
| P_dist | 0.700 | 0.718 | **+1.8 pts** |
| P_rank | 0.776 | 0.791 | **+1.5 pts** |
| P_refuse | 0.992 | 0.994 | **+0.2 pts** |
| Parse failures | 0.1% | 0.0% | -0.1 pts |

**Althing (GPT-6 Luna)** (product) on subpop — n=100 questions × 30 samples per arm, refusal detector v3; the arms differ only in elicitation mode:

| Metric | Natural | Structured | Δ (structured − natural) |
|--------|---------|------------|--------------------------|
| SPS | 0.802 | 0.791 | **-1.1 pts** |
| P_dist | 0.696 | 0.666 | **-3.0 pts** |
| P_rank | 0.730 | 0.727 | **-0.3 pts** |
| P_refuse | 0.980 | 0.980 | **+0.0 pts** |
| Parse failures | 0.3% | 0.0% | -0.3 pts |

**Althing (Haiku 5.5)** (product) on subpop — n=100 questions × 30 samples per arm, refusal detector v4; the arms differ only in elicitation mode:

| Metric | Natural | Structured | Δ (structured − natural) |
|--------|---------|------------|--------------------------|
| SPS | 0.783 | 0.791 | **+0.7 pts** |
| P_dist | 0.645 | 0.636 | **-0.9 pts** |
| P_rank | 0.731 | 0.756 | **+2.5 pts** |
| P_refuse | 0.974 | 0.980 | **+0.6 pts** |
| Parse failures | 0.8% | 0.0% | -0.8 pts |

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
| Republican | 0.683 | **0.105 ± 0.020** | 4 |
| Democrat | 0.667 | **0.052 ± 0.022** | 4 |

#### INCOME

| Group | P_dist | P_cond | Replications |
|-------|--------|--------|--------------|
| <$30K | 0.652 | **0.071 ± 0.014** | 4 |
| $100K+ | 0.673 | **0.044 ± 0.029** | 4 |

#### EDUCATION

| Group | P_dist | P_cond | Replications |
|-------|--------|--------|--------------|
| Less than HS | 0.652 | **0.087 ± 0.028** | 4 |
| College graduate | 0.684 | **0.040 ± 0.023** | 4 |

Republican conditioning is **2.0× stronger** than Democrat (mean P_cond across replications).
High-income conditioning is **1.6× stronger** than low-income.

#### Other measured attributes

| Attribute | Group | P_dist | P_cond | Replications |
|-----------|-------|--------|--------|--------------|
| CREGION | South | 0.658 | 0.060 ± 0.022 | 4 |
| CREGION | Northeast | 0.677 | 0.056 ± 0.034 | 4 |
| SEX | Male | 0.683 | 0.052 ± 0.038 | 4 |
| SEX | Female | 0.657 | 0.051 ± 0.033 | 4 |
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
| globalopinionqa (100q) | 0.799 (Althing (Qwen 3.8 Flash), product) | **0.810** | **+1.1 pts** | 0.774 (n=100) |
| globalopinionqa (100q) | 0.799 (Althing (Qwen 3.8 Flash), product) | **0.831** | **+3.1 pts** | 0.774 (n=100) |
| globalopinionqa (100q) | 0.799 (Althing (Qwen 3.8 Flash), product) | **0.818** | **+1.9 pts** | 0.774 (n=100) |
| globalopinionqa (100q) | 0.799 (Althing (Qwen 3.8 Flash), product) | **0.825** | **+2.6 pts** | 0.774 (n=100) |
| globalopinionqa (100q) | 0.799 (Althing (Qwen 3.8 Flash), product) | **0.817** | **+1.8 pts** | 0.774 (n=100) |
| gss (75q) | 0.849 (Althing (Qwen 3.8 Flash), product) | **0.816** | **-3.3 pts** | 0.735 (n=75) |
| gss (75q) | 0.849 (Althing (Qwen 3.8 Flash), product) | **0.863** | **+1.4 pts** | 0.735 (n=75) |
| gss (75q) | 0.849 (Althing (Qwen 3.8 Flash), product) | **0.848** | **-0.2 pts** | 0.735 (n=75) |
| gss (75q) | 0.849 (Althing (Qwen 3.8 Flash), product) | **0.851** | **+0.2 pts** | 0.735 (n=75) |
| gss (75q) | 0.849 (Althing (Qwen 3.8 Flash), product) | **0.845** | **-0.4 pts** | 0.735 (n=75) |
| opinionsqa (100q) | 0.874 (DeepSeek V4.1 Flash, raw) | **0.871** | **-0.3 pts** | 0.763 (n=684) |
| opinionsqa (100q) | 0.874 (DeepSeek V4.1 Flash, raw) | **0.913** | **+3.9 pts** | 0.763 (n=684) |
| opinionsqa (100q) | 0.874 (DeepSeek V4.1 Flash, raw) | **0.897** | **+2.3 pts** | 0.763 (n=684) |
| opinionsqa (100q) | 0.874 (DeepSeek V4.1 Flash, raw) | **0.906** | **+3.2 pts** | 0.763 (n=684) |
| opinionsqa (100q) | 0.874 (DeepSeek V4.1 Flash, raw) | **0.891** | **+1.7 pts** | 0.763 (n=684) |
| subpop (100q) | 0.838 (DeepSeek V4.1 Flash, raw) | **0.823** | **-1.4 pts** | 0.757 (n=200) |
| subpop (100q) | 0.838 (DeepSeek V4.1 Flash, raw) | **0.865** | **+2.7 pts** | 0.757 (n=200) |
| subpop (100q) | 0.838 (DeepSeek V4.1 Flash, raw) | **0.846** | **+0.8 pts** | 0.757 (n=200) |
| subpop (100q) | 0.838 (DeepSeek V4.1 Flash, raw) | **0.856** | **+1.9 pts** | 0.757 (n=200) |
| subpop (100q) | 0.838 (DeepSeek V4.1 Flash, raw) | **0.859** | **+2.2 pts** | 0.757 (n=200) |

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
**globalopinionqa** (n=100 common questions, mean pairwise r = 0.528):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 4.5) ↔ Althing (Gemini Flash Lite) | 0.510 | 100 |
| Althing (Haiku 4.5) ↔ Althing (GPT-4o-mini) | 0.576 | 100 |
| Althing (Gemini Flash Lite) ↔ Althing (GPT-4o-mini) | 0.498 | 100 |

**globalopinionqa** (n=100 common questions, mean pairwise r = 0.538):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Qwen 3.8 Flash) ↔ Althing (Sonnet 4) | 0.622 | 100 |
| Althing (Qwen 3.8 Flash) ↔ DeepSeek V4.1 Flash | 0.450 | 100 |
| Althing (Qwen 3.8 Flash) ↔ Gemini Flash Lite | 0.470 | 100 |
| Althing (Sonnet 4) ↔ DeepSeek V4.1 Flash | 0.483 | 100 |
| Althing (Sonnet 4) ↔ Gemini Flash Lite | 0.609 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini Flash Lite | 0.593 | 100 |

**globalopinionqa** (n=100 common questions, mean pairwise r = 0.550):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 5.5) ↔ Llama 3.3 70B | 0.647 | 100 |
| Althing (Haiku 5.5) ↔ Gemini Flash Lite | 0.455 | 100 |
| Llama 3.3 70B ↔ Gemini Flash Lite | 0.548 | 100 |

**globalopinionqa** (n=100 common questions, mean pairwise r = 0.493):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 5.5) ↔ DeepSeek V4.1 Flash | 0.431 | 100 |
| Althing (Haiku 5.5) ↔ Gemini Flash Lite | 0.455 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini Flash Lite | 0.593 | 100 |

**globalopinionqa** (n=100 common questions, mean pairwise r = 0.535):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Qwen 3.8 Flash ↔ DeepSeek V4.1 Flash | 0.497 | 100 |
| Qwen 3.8 Flash ↔ Gemini 3.5 Flash-Lite | 0.461 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini 3.5 Flash-Lite | 0.646 | 100 |

**gss** (n=75 common questions, mean pairwise r = 0.633):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 4.5) ↔ Althing (Gemini Flash Lite) | 0.601 | 75 |
| Althing (Haiku 4.5) ↔ Althing (GPT-4o-mini) | 0.617 | 75 |
| Althing (Gemini Flash Lite) ↔ Althing (GPT-4o-mini) | 0.680 | 75 |

**gss** (n=75 common questions, mean pairwise r = 0.530):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Qwen 3.8 Flash) ↔ Althing (Sonnet 4) | 0.632 | 75 |
| Althing (Qwen 3.8 Flash) ↔ DeepSeek V4.1 Flash | 0.582 | 75 |
| Althing (Qwen 3.8 Flash) ↔ Gemini Flash Lite | 0.462 | 75 |
| Althing (Sonnet 4) ↔ DeepSeek V4.1 Flash | 0.619 | 75 |
| Althing (Sonnet 4) ↔ Gemini Flash Lite | 0.486 | 75 |
| DeepSeek V4.1 Flash ↔ Gemini Flash Lite | 0.398 | 75 |

**gss** (n=75 common questions, mean pairwise r = 0.546):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 5.5) ↔ Llama 3.3 70B | 0.591 | 75 |
| Althing (Haiku 5.5) ↔ Gemini Flash Lite | 0.517 | 75 |
| Llama 3.3 70B ↔ Gemini Flash Lite | 0.532 | 75 |

**gss** (n=75 common questions, mean pairwise r = 0.461):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 5.5) ↔ DeepSeek V4.1 Flash | 0.468 | 75 |
| Althing (Haiku 5.5) ↔ Gemini Flash Lite | 0.517 | 75 |
| DeepSeek V4.1 Flash ↔ Gemini Flash Lite | 0.398 | 75 |

**gss** (n=75 common questions, mean pairwise r = 0.604):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Qwen 3.8 Flash ↔ DeepSeek V4.1 Flash | 0.667 | 75 |
| Qwen 3.8 Flash ↔ Gemini 3.5 Flash-Lite | 0.644 | 75 |
| DeepSeek V4.1 Flash ↔ Gemini 3.5 Flash-Lite | 0.500 | 75 |

**opinionsqa** (n=100 common questions, mean pairwise r = 0.498):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 4.5) ↔ Althing (Gemini Flash Lite) | 0.518 | 100 |
| Althing (Haiku 4.5) ↔ Althing (GPT-4o-mini) | 0.360 | 100 |
| Althing (Gemini Flash Lite) ↔ Althing (GPT-4o-mini) | 0.618 | 100 |

**opinionsqa** (n=100 common questions, mean pairwise r = 0.411):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Qwen 3.8 Flash) ↔ Althing (Sonnet 4) | 0.562 | 100 |
| Althing (Qwen 3.8 Flash) ↔ DeepSeek V4.1 Flash | 0.398 | 100 |
| Althing (Qwen 3.8 Flash) ↔ Gemini Flash Lite | 0.345 | 100 |
| Althing (Sonnet 4) ↔ DeepSeek V4.1 Flash | 0.468 | 100 |
| Althing (Sonnet 4) ↔ Gemini Flash Lite | 0.390 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini Flash Lite | 0.300 | 100 |

**opinionsqa** (n=100 common questions, mean pairwise r = 0.384):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 5.5) ↔ Llama 3.3 70B | 0.432 | 100 |
| Althing (Haiku 5.5) ↔ Gemini Flash Lite | 0.232 | 100 |
| Llama 3.3 70B ↔ Gemini Flash Lite | 0.486 | 100 |

**opinionsqa** (n=100 common questions, mean pairwise r = 0.318):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 5.5) ↔ DeepSeek V4.1 Flash | 0.422 | 100 |
| Althing (Haiku 5.5) ↔ Gemini Flash Lite | 0.232 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini Flash Lite | 0.300 | 100 |

**opinionsqa** (n=100 common questions, mean pairwise r = 0.403):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Qwen 3.8 Flash ↔ DeepSeek V4.1 Flash | 0.322 | 100 |
| Qwen 3.8 Flash ↔ Gemini 3.5 Flash-Lite | 0.329 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini 3.5 Flash-Lite | 0.558 | 100 |

**subpop** (n=100 common questions, mean pairwise r = 0.353):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 4.5) ↔ Althing (Gemini Flash Lite) | 0.231 | 100 |
| Althing (Haiku 4.5) ↔ Althing (GPT-4o-mini) | 0.388 | 100 |
| Althing (Gemini Flash Lite) ↔ Althing (GPT-4o-mini) | 0.439 | 100 |

**subpop** (n=100 common questions, mean pairwise r = 0.523):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Qwen 3.8 Flash) ↔ Althing (Sonnet 4) | 0.685 | 100 |
| Althing (Qwen 3.8 Flash) ↔ DeepSeek V4.1 Flash | 0.587 | 100 |
| Althing (Qwen 3.8 Flash) ↔ Gemini Flash Lite | 0.562 | 100 |
| Althing (Sonnet 4) ↔ DeepSeek V4.1 Flash | 0.468 | 100 |
| Althing (Sonnet 4) ↔ Gemini Flash Lite | 0.490 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini Flash Lite | 0.343 | 100 |

**subpop** (n=100 common questions, mean pairwise r = 0.310):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 5.5) ↔ Llama 3.3 70B | 0.289 | 100 |
| Althing (Haiku 5.5) ↔ Gemini Flash Lite | 0.230 | 100 |
| Llama 3.3 70B ↔ Gemini Flash Lite | 0.412 | 100 |

**subpop** (n=100 common questions, mean pairwise r = 0.251):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Althing (Haiku 5.5) ↔ DeepSeek V4.1 Flash | 0.178 | 100 |
| Althing (Haiku 5.5) ↔ Gemini Flash Lite | 0.230 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini Flash Lite | 0.343 | 100 |

**subpop** (n=100 common questions, mean pairwise r = 0.452):

| Constituent pair | Pearson r (per-question JSD) | n |
|------------------|------------------------------|---|
| Qwen 3.8 Flash ↔ DeepSeek V4.1 Flash | 0.467 | 100 |
| Qwen 3.8 Flash ↔ Gemini 3.5 Flash-Lite | 0.508 | 100 |
| DeepSeek V4.1 Flash ↔ Gemini 3.5 Flash-Lite | 0.380 | 100 |

The constituents' errors are **moderately positively correlated** (pairwise r 0.18–0.68 on per-question JSD; 0.27–0.44 on signed per-option residuals, see asserted constants) — not uncorrelated. The ensemble gain comes from partial, not full, independence of errors; the earlier "uncorrelated errors" framing overstated it.

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
| 1.0 | 0.830 | 1 |
| 1.2 | 0.835 | 1 |
| 1.5 | 0.834 | 1 |
| 1.8 | 0.841 | 1 |
| **2.0** | **0.841** | 1 |
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
| **Ensemble blending** | +-0.2–7.1 | zero | done |
| **Per-model optimal temperature** | +1.5–4.5 | low | actionable |
| **Demographic conditioning** | +4.0–10.5 | moderate | scientific |
| **Persona template** | 'current' template already optimal (+5.8 pts over the best alternative); no further gain available from this lever. | zero | done |
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
| Muse Glimmer 30B | raw | default | gss | 0.743 | 0.054 | **0.697** | 75 |
| Gemini 3.8 Flash | raw | default | gss | 0.719 | 0.054 | **0.679** | 75 |
| GPT-6 Luna | raw | default | gss | 0.322 | 0.054 | **0.309** | 75 |
| GPT-6 Luna | raw | default | gss | 0.243 | 0.054 | **0.250** | 75 |
| Claude Haiku 5.5 | raw | default | gss | 0.227 | 0.054 | **0.231** | 75 |
| Claude Sonnet 4 | raw | default | gss | 0.226 | 0.054 | **0.230** | 75 |
| Claude Sonnet 5.5 | raw | default | gss | 0.200 | 0.054 | **0.210** | 75 |
| Claude Haiku 4.5 | raw | default | gss | 0.176 | 0.054 | **0.190** | 75 |
| Althing (Sonnet 5.5) | product | default | gss | 0.174 | 0.054 | **0.174** | 75 |
| Althing (GPT-6 Luna) | product | default | gss | 0.156 | 0.054 | **0.153** | 75 |
| Gemini 2.5 Flash | raw | default | gss | 0.098 | 0.054 | **0.124** | 75 |
| Claude Sonnet 4.6 | raw | default | gss | 0.089 | 0.054 | **0.124** | 75 |
| Althing (Haiku 4.5) | product | structured | gss | 0.064 | 0.054 | **0.094** | 75 |
| Althing (Haiku 4.5) | product | default | gss | 0.067 | 0.054 | **0.092** | 75 |
| GPT-4o | raw | default | gss | 0.067 | 0.054 | **0.090** | 75 |
| Althing (Haiku 5.5) | product | default | gss | 0.044 | 0.054 | **0.080** | 75 |
| Gemini 3.5 Flash-Lite | raw | default | gss | 0.041 | 0.054 | **0.076** | 75 |
| Althing (GPT-6 Luna) | product | default | gss | 0.046 | 0.054 | **0.073** | 75 |
| Althing (Gemini Flash Lite) | product | default | gss | 0.035 | 0.054 | **0.073** | 75 |
| Althing (Muse Glimmer 30B) | product | default | gss | 0.034 | 0.054 | **0.070** | 75 |
| Gemini Flash Lite | raw | default | gss | 0.036 | 0.054 | **0.070** | 75 |
| GPT-4o-mini | raw | default | gss | 0.025 | 0.054 | **0.069** | 75 |
| DeepSeek V4.1 Flash | raw | default | gss | 0.027 | 0.054 | **0.068** | 75 |
| Qwen 3.8 Flash | raw | default | gss | 0.028 | 0.054 | **0.063** | 75 |
| Althing (DeepSeek V4.1 Flash) | product | default | gss | 0.019 | 0.054 | **0.062** | 75 |
| Althing (Sonnet 4.6) | product | default | gss | 0.013 | 0.054 | **0.061** | 75 |
| Althing (Gemini 3.5 Flash-Lite) | product | default | gss | 0.013 | 0.054 | **0.061** | 75 |
| Llama 3.3 70B | raw | default | gss | 0.014 | 0.054 | **0.061** | 75 |
| Althing (Sonnet 4) | product | default | gss | 0.015 | 0.054 | **0.059** | 75 |
| Althing (GPT-4o-mini) | product | default | gss | 0.016 | 0.054 | **0.059** | 75 |
| Althing (Qwen 3.8 Flash) | product | default | gss | 0.031 | 0.054 | **0.056** | 75 |
| Althing (Llama 3.3 70B) | product | default | gss | 0.002 | 0.054 | **0.052** | 75 |

Comparison set: Per deduped non-baseline run whose committed per-question rows still carry human_distribution (full-tier datasets; gated files are stripped per #308): mean |model explicit-nonresponse mass (DK-style option mass + parsed refusal rate) - human's|, plus the five items with the largest model over-selection.

**Safety-aligned models over-select explicit nonresponse options on sensitive items** (Muse Glimmer 30B, gss, n=75): mean model nonresponse mass 0.738 vs human 0.026. Worst items:

| Item | Model nonresponse | Human nonresponse |
|------|-------------------|-------------------|
| GSS_CONFINAN | 100% | 0.7% |
| GSS_XMARSEX | 100% | 0.8% |
| GSS_PORNLAW | 100% | 0.9% |
| GSS_CLASS | 100% | 1.1% |
| GSS_CONJUDGE | 100% | 1.4% |

Share of answers that pick a listed 'don't know'-style option, excluding prose refusals. The model selects a legitimate option rather than refusing, so refusal-rate metrics miss it and it only shows in the option distribution.
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
