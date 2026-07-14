# Private holdout split

**Status:** shipped — `synthbench.private_holdout` + server-side recompute in
process-submission + the `verification_badge` on every leaderboard row
**Tracking:** [issue #259](https://github.com/DataViking-Tech/SynthBench/issues/259)

## Why

The public leaderboard's headline metric is computed against per-question
human distributions. Once those distributions are visible, two failure modes
open up:

1. **Fabrication.** A submitter could construct a run JSON that copies the
   public distributions verbatim and post a near-perfect score without ever
   calling a model.
2. **Casual overfitting / contamination.** A contributor can tune a config
   against the visible answer key, and future LLMs may train on SynthBench
   itself.

Kaggle's private-leaderboard split addresses the same problem: hold back a
slice of the answer key, score it server-side, and treat public/private
divergence as the trust signal. That is what ships here.

## The shipped mechanism

### The split (`src/synthbench/private_holdout.py`)

Each holdout-enabled dataset is deterministically partitioned by hashing
`base_dataset_name + ":" + question_key` with **unsalted SHA-256**; the first
8 hex digits mod 100 give a bucket, and buckets below the dataset's private
fraction are private. The fraction is per-dataset, calibrated by dataset size
(power analysis in `docs/benchmark-hardening-analysis.md` §4.2):

| Datasets                              | Private fraction |
| ------------------------------------- | ---------------- |
| opinionsqa, wvs, gss (large, N ≥ 500)  | 20%              |
| subpop, globalopinionqa (medium)       | 30%              |
| michigan, ntia, eurobarometer (small)  | 40%              |

`pewtech` is excluded: it ships citation-only, so its entire human
distribution is already suppressed and a holdout adds nothing.

Properties:

- **Deterministic** — same `(dataset, key)` → same partition across runs,
  machines, and Python versions. No seed file, no state.
- **Dataset-scoped** — shared keys across datasets partition independently.
- **Adapter-free** — publish and validation can classify any
  `(dataset, key)` pair without loading the dataset adapter.

### What is withheld — and what is not

**Holdout *membership* is public.** The hash is unsalted and this repository
is public, so anyone can compute which questions are private
(`is_private_holdout(dataset, key)`); published run artifacts even carry
explicit `is_holdout: true` flags on private rows. This is intentional and
Kaggle-like: contributors need to know the split exists and how big it is.

**The *answer key* is what is withheld.** For private-holdout questions, the
per-question human distributions are:

- absent from every committed `leaderboard-results/*.json` (submissions are
  stripped of `human_distribution` before commit);
- absent from every published artifact — run detail JSON, config pages, and
  question-explorer pages (private questions get no question page at all);
- stored canonically only in the gated R2 origin
  (`human-distributions/<dataset>.json`) and credentialed maintainer caches
  (`~/.synthbench/human-distributions/`). The public data proxy Worker
  allowlists only `run/`, `config/`, and `question/` paths, so
  `human-distributions/*` is unroutable even for authenticated users.

The pip wheel ships **zero raw data** — `[tool.setuptools.package-data]` is
deliberately unset (see the comment in `pyproject.toml`); adapters fetch
upstream data at runtime.

### Server-side scoring (process-submission)

Submissions **must include results for every question, public and private** —
public-only submissions are rejected at validation, with a plausibility check
that the submission's private fraction matches the expected per-dataset
fraction.

The submitter's self-reported holdout metrics are never trusted. The
process-submission pipeline runs tier-3 validation with
`--rehydrate-canonical` under R2 credentials: every row's
`human_distribution` is **replaced** with the canonical value from the gated
artifact, and per-question JSD/τ are recomputed against that canonical answer
key (bounded by the recompute tolerance, ~1e-2 per question).

### The verification badge

At publish time, `compute_split_sps` produces `sps_public`, `sps_private`,
and `sps_public_private_delta` for each entry. Rows whose delta is within
`SPS_DIVERGENCE_THRESHOLD` (0.05; typical honest deltas are < 0.02) earn a
**✓ verified** badge; rows outside it are **⚠ flagged** — held for review,
not proof of cheating. Every leaderboard entry on a holdout-enabled dataset
carries one of the two badges. See the methodology page's "Private holdout
split" section for the contributor-facing explainer.

## Honest threat model — what this split does and does not protect against

The private holdout is a **fabrication detector and a lazy-overfitting
deterrent, not cryptographic secrecy.**

- Holdout membership is publicly computable (see above). That is fine: the
  protection comes from withholding the answer key, not the question list.
- **The upstream caveat:** the source datasets (Pew, GlobalOpinionQA, WVS,
  GSS, etc.) are publicly downloadable, and the adapters in this repository
  will rebuild the full per-question human distributions — including the
  private subset — for anyone willing to run them. A determined actor can
  therefore reconstruct the private targets. The split raises the effort bar
  from "copy the published JSON" to "download and process the upstream
  source", which defeats casual fabrication and catches copied-answer-key
  submissions, but it cannot stop a motivated adversary.
- A genuinely un-memorizable holdout requires **newly fielded human data**
  (fresh survey waves not present in any public corpus) on a rotation
  cadence. That is a data-acquisition program, not a code change, and is
  scoped separately from #259.

## Verifying your score (the reproducibility tension)

Contributors cannot read the private answer key, but they can verify the
pipeline:

- Both halves of your submission are echoed back as scores: `sps_public`,
  `sps_private`, and the delta are published on your row.
- The public subset is fully recomputable from public artifacts using the
  same open-source metric code, so you can confirm the scoring math on the
  half you *can* see.
- The server-side recompute replaces distributions for **all** rows (public
  and private) from the same canonical artifact, so agreement on the public
  half is evidence the private half was scored by the same machinery.

This is the "score + cell counts, not raw items" resolution sketched in
issue #259.

## History

An earlier, never-deployed seed-based split (`synthbench.datasets.split`,
25% on pewtech + globalopinionqa, `synthbench run --held-out` gated by a
`SYNTHBENCH_HELD_OUT_AUTH` env var) was removed in the PR that closed #259.
It produced a partition inconsistent with the shipped hash-based split
(e.g. 25% seeded vs. 30% hash-based on globalopinionqa), and nothing
server-side ever invoked it. The leaderboard schema still reserves
`sps_held_out` / `held_out_badge` fields for a possible future periodic
re-evaluation job; no current pipeline populates them, and whether such a
cron is still wanted (submission-time server-side scoring largely supersedes
it) is an open design decision.

## Related

- `src/synthbench/private_holdout.py` — the split + divergence computation.
- `docs/benchmark-hardening-analysis.md` §4.2 — power analysis behind the
  per-dataset fractions.
- `site/src/components/methodology/PrivateHoldoutSection.astro` — the
  contributor-facing methodology explainer.
- Issue #257 — user-supplied configurations on the leaderboard.
- Issue #259 — this work.
