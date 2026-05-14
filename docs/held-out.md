# Held-out validation split

**Author:** automation (issue #259)
**Status:** initial implementation — server-side periodic re-eval + trust badge are follow-ups
**Tracking:** [issue #259](https://github.com/DataViking-Tech/SynthBench/issues/259)

## Why

The public leaderboard's headline metric is computed against data
contributors can see. Once user-supplied configurations (issue #257) become
first-class leaderboard entries, that's gameable: a contributor can tune
their config so it overfits the visible Pew ATP / GlobalOpinionQA sample
without generalising.

Kaggle solved this with a private leaderboard. We do the same: a held-out
slice of the eval data is hidden from contributors and the public
benchmark, and the leaderboard re-evaluates top configs against it on a
schedule. Divergence between public and held-out scores becomes the
trust signal for that row.

## What's in this initial cut

This PR ships the foundations only:

1. **The deterministic split.** `synthbench.datasets.split.make_split` and
   `is_held_out` produce a stable public/held-out partition keyed off
   `sha256(item_id + ":" + seed)`. The same item lands in the same
   partition across runs, machines, and Python versions.
2. **The runner gate.** `synthbench run --held-out` evaluates against the
   held-out cut. Default behaviour (no flag) evaluates against the
   public cut.
3. **The env-var lock.** `--held-out` requires
   `SYNTHBENCH_HELD_OUT_AUTH` to be set. This is the placeholder for the
   future shared-secret gate that protects the held-out cut from being
   leaked through accidental CI invocations.

Out of scope for this PR (tracked as follow-ups on #259):

- Server-side periodic re-eval cron.
- The trust-badge UI on leaderboard rows (✓ green / ⚠ yellow / ✗ red).
- The Δ-threshold calibration that decides red vs. yellow. The
  `private_holdout` module already uses `0.05` for its sibling
  cheat-detector metric; that's a reasonable placeholder until the
  held-out worker has enough runs to set the threshold empirically.

## How the split works

```python
from synthbench.datasets.split import make_split, is_held_out

items = [{"id": "q_001", "text": "..."}, {"id": "q_002", "text": "..."}]
public, held_out = make_split(items, seed=0x53594E54, held_out_frac=0.25)

# Equivalent, O(1):
assert is_held_out("q_001", seed=0x53594E54, held_out_frac=0.25)  # maybe
```

Internals:

1. Each item gets a `_split_id` = `sha256(id + ":" + seed)` (hex).
2. The first 8 hex chars are interpreted as a 32-bit integer and reduced
   modulo `10_000_000`.
3. Buckets strictly less than `held_out_frac * 10_000_000` are held-out.

This gives us:

- **Determinism** — same `(id, seed)` → same partition, every time.
- **Order-independence** — re-ordering the input items doesn't change
  the partition.
- **Stability under content edits** — adding new items or fixing typos
  in question text doesn't reshuffle the partition, because the hash
  keys off the item id only.
- **Cheap classification** — `is_held_out` is a single SHA-256 +
  integer compare; no need to materialise the split to answer "is this
  one item held out?"

The canonical seed is `DEFAULT_HELD_OUT_SEED = 0x53594E54` (an arbitrary
string-derived constant; see source comment). The seed is pinned because
bumping it reshuffles every partition decision and invalidates all
previously-scored held-out runs. The held-out fraction is 25% by default
to match the upper end of the 20-30% range floated in #259.

## Datasets in scope

The runner-side filter applies to the two datasets called out in #259:

- `pewtech` — Pew American Trends Panel.
- `globalopinionqa` — GlobalOpinionQA.

Other datasets are untouched by the `--held-out` flag (they behave
exactly as before). The explicit allow-list lives in
`HELD_OUT_ENABLED_DATASETS` in `src/synthbench/datasets/split.py`.

There is a related but distinct module — `synthbench.private_holdout` —
that powers the *publish*-time cheat-detector SPS delta. That module has
its own per-dataset fraction map (`HOLDOUT_ENABLED_DATASETS`) and is
already wired into shipped leaderboard rows. The two modules will
likely be unified in a future PR; we keep them separate for now so this
change doesn't disturb already-scored runs.

## Migration & shipped scores

The semantics of the **default** `synthbench run` change for the two
held-out-enabled datasets:

- **Before this PR:** `synthbench run -d globalopinionqa` evaluated all
  questions.
- **After this PR:** `synthbench run -d globalopinionqa` evaluates the
  *public* cut only (~75% of items).

For the other seven datasets, default behaviour is unchanged.

**Shipped leaderboard rows are not retroactively rescored.** They were
produced against the pre-PR "all items" cut and remain valid as
historical records. New submissions on Pew ATP / GlobalOpinionQA after
this PR ships will be on the public cut and are not directly comparable
to those historical scores — the leaderboard UI should annotate the
cutoff. (Tracked as a follow-up; the existing publish pipeline doesn't
distinguish "all" vs "public" today.)

## The reproducibility tension

The unresolved question in #259 was: how does a contributor verify their
held-out score was computed correctly if they can't see the held-out
items?

The sketched answer — to be fleshed out in a follow-up PR — is:

1. The held-out worker publishes per-question **cell counts** (n
   samples, n correct, JSD/τ values) for the contributor's run against
   the held-out cut. These cell counts identify which questions were
   scored without revealing the question text or human distribution.
2. The contributor can recompute SPS from those cell counts using the
   public-domain metric code and confirm it matches the headline
   held-out score.
3. The contributor can also recompute their *public* SPS the same way
   and confirm both reductions agree on the public subset, building
   trust in the held-out pipeline by inspection.

This is the "score + cell counts, not raw items" resolution sketched in
the issue. The hand-wavy parts are the schema of the cell-count
publication and the audit UI; both depend on the trust-badge work that
hasn't started yet.

## The env-var lock

`SYNTHBENCH_HELD_OUT_AUTH` is a placeholder for the production
shared-secret gate. In production, the leaderboard server will issue
rotating tokens to the periodic re-eval workers; the held-out cut data
will not be present in the pip wheel at all (it'll be downloaded from a
gated R2 bucket).

For local development, any non-empty value passes the gate. The point
of the gate today is to prevent a contributor from accidentally running
`--held-out` and overfitting to the held-out subset's structure even
without knowing the answer keys.

## API surface

```python
from synthbench.datasets.split import (
    make_split,                       # (items, seed, frac) -> (public, held_out)
    is_held_out,                      # (item_id, seed, frac) -> bool
    is_held_out_enabled_dataset,      # (name) -> bool — runner-side filter applies
    require_held_out_auth,            # raises HeldOutAuthError if env unset
    HeldOutAuthError,
    DEFAULT_HELD_OUT_SEED,
    DEFAULT_HELD_OUT_FRAC,
    HELD_OUT_AUTH_ENV,
    HELD_OUT_ENABLED_DATASETS,
)
```

## Related

- `synthbench.private_holdout` — sibling module powering the
  publish-time cheat-detector SPS delta.
- `docs/benchmark-hardening-analysis.md` §4.2 — power analysis behind
  the per-dataset fractions used by `private_holdout`.
- Issue #257 — user-supplied configurations on the leaderboard.
- Issue #259 — this work.
