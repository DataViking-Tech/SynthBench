# Datasets in SynthBench

SynthBench evaluates models against ground-truth human response distributions.
The signal-to-noise ratio of the leaderboard depends entirely on the quality of
the datasets behind it, so adding a dataset is a **gated process** — not
self-service. This document describes who decides, on what criteria, and what
happens when a dataset becomes stale.

## Current datasets

Source of truth: [`src/synthbench/datasets/`](src/synthbench/datasets/) and the
`DATASETS` registry in
[`src/synthbench/datasets/__init__.py`](src/synthbench/datasets/__init__.py).

At time of writing: `opinionsqa`, `globalopinionqa`, `subpop`, `pewtech`,
`eurobarometer`, `ntia`, `michigan`, `wvs`, `gss`.

## Why gated, not open

An open BYO-benchmark would clog the leaderboard with low-coverage,
low-representativeness, or duplicative datasets and destroy the cross-model
signal that makes SPS / JSD comparisons meaningful. The maintainer team
curates the set against the criteria below; users propose, maintainers decide.

If you need a private leaderboard against your own dataset, that is a separate
artifact and lives outside this repo.

## Inclusion criteria

Every new dataset must clear all five bars. A proposal that fails any one of
them will be declined — not deferred — until the gap is resolved. The bars
exist because a previous candidate failed on each.

### 1. Representativeness

The sampling frame must approximate a well-defined target population (general
public, registered voters of country X, healthcare professionals in country
Y, …). Convenience samples and self-selected panels are not eligible unless
the proposer can demonstrate post-stratification weighting that brings the
sample within published tolerance of the frame.

### 2. Ground-truth coverage

- **Questions:** ≥ 50 questions with a usable `human_distribution`.
- **Respondents per question:** ≥ 200 on average; ≥ 30 minimum (anything
  smaller makes the human distribution itself noisier than the model
  signal we are trying to measure).
- **Microdata strongly preferred.** Real-sampling convergence (see
  `MicrodataRow` in `src/synthbench/datasets/base.py`) requires
  per-respondent rows. Aggregates-only datasets are accepted only when
  the dataset fills a use-case gap no microdata source can.

### 3. Licensing & redistribution

The dataset must declare one of the four redistribution tiers in
`src/synthbench/datasets/base.py` (`RedistributionPolicy`):

| Tier | What ships publicly | When to use |
| --- | --- | --- |
| `full` | Per-question `human_distribution` on the static site | License is unambiguously permissive (e.g. U.S. federal works under 17 USC §105, explicit CC0) |
| `gated` | Per-question artifacts behind a JWT-authenticated R2 origin | Research-use license that requires controlled distribution |
| `aggregates_only` (default) | Aggregate metrics only; no per-question payload | Ambiguous or missing redistribution rights |
| `citation_only` | Metadata only; no aggregate metrics either | No redistribution rights at all |

The cited license text must support the chosen tier. "I think it's fine" is
not a defense; if the policy is unclear, default to `aggregates_only`.

Gating is fail-closed at publish time: `gated` artifacts ship only to the
authenticated R2 origin and are never written to the local static output.
If the publish step runs without R2 credentials, gated artifacts are
skipped with a warning (or the publish fails outright under
`--strict-gating` / `SYNTHBENCH_PUBLISH_STRICT=1`, which CI deploys set),
and `scripts/verify-publish-integrity.py` fails the build if any non-`full`
artifact is found under `site/public/data/`.

**Gated data is also never committed to the repo** (issue #308). Committed
`leaderboard-results/*.json` files for gated datasets are stripped of
per-question `human_distribution` (marker: top-level
`"stripped_fields": ["human_distribution"]`) — see
`scripts/strip-gated-distributions.py`, which the submission pipeline runs
before every commit and `scripts/verify-publish-integrity.py` +
`tests/test_strip_gated_guard.py` enforce in CI. The publish pipeline
rehydrates the distributions from the **canonical registry**
(`src/synthbench/human_distributions.py`): a local per-dataset artifact
(`~/.synthbench/human-distributions/<dataset>.json` or
`$SYNTHBENCH_HUMAN_DISTRIBUTIONS_DIR`), the gated R2 object
`human-distributions/<dataset>.json` (what CI deploys use), or the dataset
adapter's own cache. Maintainers regenerate the canonical artifacts from
the true upstream data with:

```bash
python scripts/generate-canonical-distributions.py            # local artifacts
python scripts/generate-canonical-distributions.py --upload   # + gated R2
```

Run the `--upload` form after adding a gated dataset or refreshing a wave —
strict CI deploys fail loudly when a stripped gated dataset has no
canonical source to rehydrate from.

### 4. Vertical / use-case fit

Round-2 PMF (2026-05-14) flagged the leaderboard as too narrow on general
public opinion. New datasets should fill a documented gap (see Roadmap
below) rather than duplicate an existing adapter's signal. A proposal that
overlaps an existing dataset must explain what new signal it contributes —
a different population, a different question domain, or a stricter
methodology.

### 5. Maintenance commitment

Surveys ship new waves. A proposer must name a maintainer (themselves or a
team) responsible for refreshing the adapter when a new wave lands, and
state expected cadence. Datasets with no named maintainer are subject to
the deprecation policy below.

## Maintainer review workflow

```
1. Contributor files a "New dataset proposal" issue using
   .github/ISSUE_TEMPLATE/new-dataset.md
   → automatically labeled `dataset-proposal`

2. Two-phase review:

   Phase A — Proposal review (before any code is written)
     • A maintainer triages within ~1 week.
     • Maintainer either applies `dataset-approved` (proposal cleared)
       or declines with a written reason.
     • This phase exists to spare contributors from writing an adapter
       for a dataset that will not be accepted.

   Phase B — PR review (after the approved proposal)
     • Contributor opens a PR touching `src/synthbench/datasets/**`
       and updating `DATASETS` in `src/synthbench/datasets/__init__.py`.
     • The `dataset-gating` workflow auto-labels the PR `datasets-change`
       and posts a sticky checklist comment.
     • The workflow's gate job fails CI until a maintainer applies the
       `dataset-approved` label (mirrored from the issue once code review
       passes). This is enforced from the GitHub event so the PR author
       cannot self-label.
     • Maintainer confirms representativeness, coverage, redistribution
       tier, license citation, and tests, then applies the label.

3. Refinery merges as normal once CI is green and approval is in.
```

Maintainers: see [`.github/workflows/dataset-gating.yml`](.github/workflows/dataset-gating.yml)
for the automation.

## Deprecation & retirement

Datasets are not forever. A dataset is eligible for deprecation when **any
two** of the following hold:

- The named maintainer has been unresponsive for ≥ 90 days on a wave
  refresh or a CI breakage.
- The upstream source has been withdrawn, paywalled, or relicensed in a
  way that breaks the declared redistribution tier.
- The sampling frame has changed materially (target population redefined,
  methodology overhauled) such that the existing adapter's outputs are no
  longer comparable to prior waves.
- A higher-coverage or more representative dataset has been added that
  fully subsumes the same vertical.

Deprecation process:

1. Maintainer opens a deprecation issue tagged `dataset-deprecation`
   citing which criteria triggered it.
2. The adapter is annotated `deprecated_since = "<release>"` and emits a
   one-time runtime warning on load. The dataset still scores during this
   **one-release grace period** so existing submissions do not break.
3. After the grace release, the adapter is removed from the `DATASETS`
   registry. Historical leaderboard rows that referenced it remain (data
   is not rewritten retroactively) but no new submissions can target it.

A retired dataset can be revived by a new proposal that clears the
inclusion criteria afresh.

## Roadmap

Datasets the maintainers have **approved in principle** but not yet built.
Contributions welcome — open a PR against the listed file path with the
adapter, tests, and a methodology paragraph. The proposal phase is already
cleared for items on this list.

| Slug | Vertical | Gap addressed | Status |
| --- | --- | --- | --- |
| _(healthcare professional opinion source TBD)_ | Healthcare | Round-2 PMF gap | Seeking dataset |
| _(consumer fintech sentiment, monthly)_ | Fintech | Round-2 PMF gap | Seeking dataset |
| _(in-product behavior / preference; e.g. consented panel)_ | Product behavior | Round-2 PMF gap | Seeking dataset |
| _(US regional / state-level opinion panel)_ | US regional | Round-2 PMF gap | Seeking dataset |

When you propose a roadmap candidate, prefix the issue title with
`[roadmap]` so triage knows the proposal phase is already cleared and the
review goes straight to scope / methodology.

## See also

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — general contribution workflow
- [`src/synthbench/datasets/base.py`](src/synthbench/datasets/base.py) —
  the `Dataset` interface, `RedistributionPolicy` definition, and tier
  semantics
- [`src/synthbench/datasets/policy.py`](src/synthbench/datasets/policy.py)
  — runtime resolution of redistribution policy
- [`METHODOLOGY.md`](METHODOLOGY.md) — how dataset outputs feed the
  leaderboard
