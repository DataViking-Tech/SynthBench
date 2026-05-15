# User-contributed benchmark datasets (BYO-benchmark)

> Tracks Wesley directive 2026-05-14 (Round-2 PMF synthesis §4.C), bead `sb-7je`.

A **user benchmark** lets the community contribute its own survey questions
and human ground-truth distributions to the SynthBench leaderboard. It is
the **dataset twin** of [user-configuration artifacts](configs.md): where a
user-config publishes *how* a vendor was tuned for a subgroup, a
user-benchmark publishes *what questions* the vendor is scored against. The
leaderboard then renders a new dataset slice keyed on `benchmark_id` so a
healthcare or fintech-specific benchmark stands on its own next to the
default Pew ATP / GlobalOpinionQA slices.

Round-2 PMF feedback (2026-05-14) flagged domain-specificity as the
universal "but" — buyers want healthcare, fintech, product-behaviour, and
NPS coverage. Rather than ship vertical packs in-house on a multi-quarter
cadence, this flow opens the door for the community to land verticals as
fast as they can author and validate them.

## At a glance

```bash
# 1. Author your benchmark dataset (JSON, pinned to the harness version
#    you ran on).
$EDITOR datasets/fintech-trust.json

# 2. Validate locally before submitting — every schema error is collected
#    in one pass so you can fix them all before re-running.
synthbench validate-benchmark datasets/fintech-trust.json

# 3. Submit alongside the result file produced by running your harness
#    against that dataset. The dataset is stamped onto the submission
#    body (questions hashed) so the leaderboard renders a new slice.
synthbench submit \
    --benchmark datasets/fintech-trust.json \
    results/openrouter_fintech_run.json
```

`--benchmark` composes with `--config` — a single submission can publish
both *how* the vendor was tuned and *what* it was scored against:

```bash
synthbench submit \
    --config configs/fintech-tuned.yaml \
    --benchmark datasets/fintech-trust.json \
    results/openrouter_fintech_run.json
```

## Schema

```json
{
  "benchmark_id": "fintech-trust-2026q1",
  "title": "Fintech trust survey, Q1 2026",
  "contributor": "@wesley",
  "description": "Consumer trust in fintech products.",
  "domain": "fintech",
  "harness_version": "0.1.0",
  "source": {
    "citation": "DataViking Internal Pilot, 2026-Q1",
    "license": "CC-BY-4.0",
    "url": "https://example.com/fintech-trust-2026q1"
  },
  "redistribution_policy": "aggregates_only",
  "questions": [
    {
      "key": "trust_primary_bank",
      "text": "How much do you trust your primary bank with your personal financial data?",
      "options": ["A great deal", "Some", "Not much", "Not at all"],
      "human_distribution": {
        "A great deal": 0.28,
        "Some": 0.41,
        "Not much": 0.21,
        "Not at all": 0.10
      },
      "topic": "trust"
    }
  ],
  "notes": "Optional free-form prose."
}
```

### Top-level keys (allowed set)

| Field                   | Required | Notes |
|-------------------------|----------|-------|
| `benchmark_id`          | yes      | kebab-case slug, 2–64 chars. Combined with the content hash forms the leaderboard slice identity. |
| `title`                 | yes      | Free-form. Shown on the slice header. |
| `contributor`           | yes      | GitHub `@handle` or bare email. Surfaced verbatim. |
| `description`           | yes      | Free-form prose. Shown on the slice methodology page. |
| `domain`                | yes      | kebab-case slug (`healthcare`, `fintech`, `nps`, …). Groups slices on the leaderboard sidebar. |
| `harness_version`       | yes      | The synthbench harness version this benchmark was scored against. Mismatch is fatal unless `--allow-harness-mismatch`. |
| `source`                | yes      | `{citation, license, url?}`. Required for licence audit. |
| `redistribution_policy` | yes      | One of `full`, `gated`, `aggregates_only`, `citation_only` — same enum as in-tree `synthbench.datasets.base.RedistributionPolicy`. |
| `questions`             | yes      | List of question objects, minimum 5 (below that the scoring noise drowns out the signal). |
| `notes`                 | no       | Free-form prose, optional. |

Unknown top-level keys are rejected so contributors can't smuggle opaque
fields past the leaderboard.

### Per-question shape

```json
{
  "key": "trust_primary_bank",
  "text": "How much do you trust your primary bank …?",
  "options": ["A great deal", "Some", "Not much", "Not at all"],
  "human_distribution": {
    "A great deal": 0.28,
    "Some": 0.41,
    "Not much": 0.21,
    "Not at all": 0.10
  },
  "topic": "trust"
}
```

Constraints the validator enforces:

- `key` must be unique within the file.
- `options` is a list of at least 2 distinct strings.
- Every value in `human_distribution` must be a number in `[0, 1]` and the
  total mass must sum to `1.0 ± 0.01` (same slack as the in-tree
  `Question` dataclass before it renormalises).
- Every option declared in `options` must have mass in
  `human_distribution`, and no extra labels are allowed. Silently
  omitting an option would hide a real response from the scoring pipeline.
- `topic` is optional free-form prose.

## Submit flow

`synthbench submit --benchmark <json> <run.json>` does three things in order:

1. Loads + validates the JSON. On failure, every schema error is surfaced
   in one pass (no fix-one, re-run, repeat) and the CLI exits with code 2.
2. Cross-checks `harness_version` against the installed `synthbench`. A
   mismatch is fatal unless `--allow-harness-mismatch` is passed.
3. Computes a SHA-256 hash over the canonicalised `questions` block and
   stamps the benchmark dict (plus `benchmark_hash`) onto the submission
   body as the `user_benchmark` top-level key, then POSTs to the Worker
   exactly like a plain `synthbench submit` would.

### Where it lives in the submission body

```json
{
  "benchmark": "synthbench",
  "schema_version": "...",
  "config": { "...existing provider+dataset config..." },
  "scores": { "...existing scores..." },
  "aggregate": { "..." },
  "per_question": [ "..." ],
  "user_benchmark": {
    "benchmark_id": "fintech-trust-2026q1",
    "title": "...",
    "contributor": "@wesley",
    "description": "...",
    "domain": "fintech",
    "harness_version": "0.1.0",
    "source": { "citation": "...", "license": "CC-BY-4.0", "url": "..." },
    "redistribution_policy": "aggregates_only",
    "questions": [ "..." ],
    "notes": "...",
    "benchmark_hash": "<sha256 of canonical questions block>"
  }
}
```

Like `user_config`, we keep `user_benchmark` at the top level (not inside
`config`) so the existing `config_id` hash — which only reads a fixed set
of keys under `config` — is unaffected. The new slice identity is
`benchmark_id`, distinct from the underlying provider config.

## Content hash

The `benchmark_hash` is a SHA-256 over the canonical JSON serialisation of
the **questions block only** (sorted keys, compact separators). Two
implications worth knowing as a contributor:

- Fixing a typo in `title`, `description`, or `notes` does **not** mint a
  new slice identity. The leaderboard treats the corrected re-submission
  as the same slice.
- Editing any question — adding, removing, reordering, or changing a
  distribution value — produces a new hash and therefore a new slice.
  This is deliberate: scores against different question sets are not
  comparable, and the server-side fanout that runs the benchmark against
  all current vendor configs needs a stable content identity to dedupe on.

If you want to publish a v2 of an existing benchmark, bump `benchmark_id`
explicitly (e.g. `fintech-trust-2026q1` → `fintech-trust-2026q2`) rather
than mutating the question set under the same id.

## Server-side fanout (forward reference)

Submitting a `user_benchmark` artefact is intended to trigger the Worker
to fan out and re-score the benchmark against every currently-tracked
vendor configuration, so the new slice arrives on the leaderboard already
populated rather than empty. That orchestration is downstream of this
artefact's contract and tracked under follow-up beads filed against
`sb-7je`; this module specifies the on-disk artefact + submission body so
the orchestration work has a stable schema to build against.

## Reproducibility contract

Each benchmark is a reproducible artefact pinned to:

- the harness version (`harness_version`)
- the source provenance (`source.citation` + `source.license`)
- the canonical questions block (`benchmark_hash`)

Anyone with the same harness can re-score the benchmark against any vendor
and expect the same scores (modulo sampling noise). The
`redistribution_policy` controls how much of the per-question detail can
ship publicly with those scores — same four-tier semantics as in-tree
datasets.

## Sample benchmarks

See [`templates/user-benchmarks/`](../templates/user-benchmarks/) for
ready-to-edit starting points.
