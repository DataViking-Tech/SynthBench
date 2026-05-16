---
name: New dataset proposal
about: Propose adding a new dataset to SynthBench
title: "[dataset] <name>: <one-line scope>"
labels: ["dataset-proposal"]
---

> Read [`DATASETS.md`](../../DATASETS.md) before filing. Maintainers will not
> review proposals that skip the criteria below — the questions exist because
> a previous dataset failed on one of them.

## Dataset

- **Name (slug):** <e.g. `pewglobal2024`; lowercase, no spaces>
- **Full title:**
- **Publisher / source URL:**
- **Wave(s) or vintage covered:**

## Why this dataset

Which Round-2 PMF gap or use-case does it fill (healthcare, fintech, product
behavior, US-regional, non-US/EU geography, longitudinal, …)?  If it
overlaps an existing adapter, explain what it adds that the existing one
cannot.

## Inclusion criteria

Answer each — see [`DATASETS.md`](../../DATASETS.md) §"Inclusion criteria"
for the bar.

- [ ] **Representativeness.** Sampling frame and weighting scheme; describe
  the target population and how the sample approximates it.
- [ ] **Ground-truth coverage.** Number of questions with a usable
  `human_distribution`. Target: ≥ 50 questions, ≥ 200 respondents per
  question on average.
- [ ] **Microdata available?** Required for real-sampling convergence
  analysis. If aggregates-only, justify.
- [ ] **License & redistribution tier.** One of `full`, `gated`,
  `aggregates_only`, `citation_only` — quote the license text or link that
  supports your tier choice (see `src/synthbench/datasets/base.py`
  `RedistributionPolicy`).
- [ ] **Citation.** Canonical citation string for the methodology page.
- [ ] **Vertical / use-case fit.** Which leaderboard segments would this
  enrich? (general public opinion / healthcare / fintech / product /
  regional)
- [ ] **Maintenance commitment.** Who refreshes this when a new wave
  ships, and how often does it ship?

## Risks / known issues

- Sensitive content, redistribution ambiguity, sampling caveats,
  question-wording asymmetries vs. existing datasets, etc.

## Proposed adapter

- File path: `src/synthbench/datasets/<slug>.py`
- Class name: `<Slug>Dataset`
- Will subclass: `synthbench.datasets.base.Dataset`
- Provides microdata? (yes / no)

## Implementation plan

Brief sketch of how `load_questions()` (and `load_microdata()` if applicable)
will work, where the source data lives, and any preprocessing required.

---

Maintainer checklist (do not fill — for reviewer):

- [ ] Proposal meets all inclusion criteria
- [ ] Redistribution tier is defensible from the cited license
- [ ] No duplication of existing dataset's signal
- [ ] Approved → label `dataset-approved` applied; PR may proceed
