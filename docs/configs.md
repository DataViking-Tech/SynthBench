# User-configuration artifacts

> Tracks Wesley directive 2026-05-14, [GH#257](https://github.com/DataViking-Tech/SynthBench/issues/257), bead `sb-vgb`.

A **user configuration** lets a contributor publish *how they tuned a vendor*
for a specific subgroup — system prompts, persona packs, decoding knobs,
ensemble weights — alongside the result it produces. The leaderboard then
treats each `{vendor}/{config_name}` pair as its own row, so a community
contribution targeting "healthcare workers in NC/MN/WI/IA" can stand on its
own next to the vendor's default settings and win on the slice it cares
about.

This document describes the schema, the validator, the submit flow, and
what makes a config artifact reproducible.

## At a glance

```bash
# 1. Author your config (YAML, pinned to the harness version you ran on).
$EDITOR configs/healthcare-northcentral.yaml

# 2. Validate locally before submitting.
synthbench validate-config configs/healthcare-northcentral.yaml

# 3. Submit alongside your benchmark result. The config is stamped onto
#    the submission body and the leaderboard renders a {vendor}/{config_name}
#    row instead of bare {vendor}.
synthbench submit \
    --config configs/healthcare-northcentral.yaml \
    results/synthpanel_healthcare_run.json
```

## Schema

```yaml
# Required. Vendor adapter the result was produced against. Must match a
# registered vendor; the leaderboard groups rows by this field.
vendor: synthpanel

# Required. Free-form version string the contributor declares. Reported on
# the leaderboard row so two configs against different vendor releases stay
# distinguishable.
vendor_version: "1.4.0"

# Required. kebab-case slug, 2–64 chars, ASCII. Combined with `vendor` to
# form the leaderboard row identity.
config_name: "wesley-healthcare-northcentral"

# Required. Contact handle for the contributor. GitHub-style "@username"
# or a bare email. Surfaced verbatim on the leaderboard.
contributor: "@wesley"

# Required. The synthbench harness version this config was produced against
# (e.g. "0.1.0"). The submit flow refuses mismatches by default — pass
# --allow-harness-mismatch to override deliberately.
harness_version: "0.1.0"

# Required. The slice this config targets. `description` is free-form prose
# shown on the row. `selector` is optional machine-checkable criteria the
# leaderboard uses to compute the win-region highlight (where this config
# beats the vendor's default on the targeted subgroup).
target_subgroup:
  description: "Healthcare workers in NC, MN, WI, IA"
  selector:
    geography: ["NC", "MN", "WI", "IA"]
    occupation: ["healthcare"]

# Optional. Persona-pack identifiers the adapter should compose.
packs: ["healthcare-patient", "general-consumer"]

# Optional. Per-pack ensemble weights (same length as `packs`). Non-negative
# and must sum to 1.0 within 1e-3.
ensemble_weights: [0.7, 0.3]

# Optional. Free-form system / template overrides the adapter accepts. Each
# key is a prompt-slot name; each value is the string to substitute.
extra_prompts:
  system: |
    You are responding as a healthcare professional in a Midwest US setting.
    Reflect realistic concerns about staffing, scheduling, and EHR friction.

# Optional. Decoding-knob overrides. `temperature` must be non-negative;
# `top_p` must be in [0, 1]. Other keys (model, top_k, ...) pass through.
decoding:
  temperature: 0.6
  top_p: 0.9
  model: "anthropic/claude-haiku-4-5"

# Optional. Free-form note shown under the row. Don't paste secrets here —
# everything in the artifact is public on the leaderboard.
notes: |
  Optimized for healthcare workers in NC/MN/WI/IA. Beats synthpanel/default
  by ~6 pp on the targeted slice; tie elsewhere.
```

### Top-level keys (allowed set)

| Key                 | Type           | Required | Notes                                            |
|---------------------|----------------|----------|--------------------------------------------------|
| `vendor`            | string (slug)  | ✓        | kebab-case ASCII, 2–64 chars                     |
| `vendor_version`    | string         | ✓        | free-form                                        |
| `config_name`       | string (slug)  | ✓        | kebab-case ASCII, 2–64 chars                     |
| `contributor`       | string         | ✓        | `@handle` or `name@example.com`                  |
| `harness_version`   | string         | ✓        | matched against installed `synthbench.__version__` |
| `target_subgroup`   | mapping        | ✓        | `description` required; `selector` optional      |
| `packs`             | list[string]   | optional | non-empty when present                           |
| `ensemble_weights`  | list[number]   | optional | non-negative, sums to 1.0; matches `packs` length |
| `extra_prompts`     | mapping        | optional | string keys → string values                      |
| `decoding`          | mapping        | optional | `temperature` ≥ 0, `top_p` ∈ [0, 1]              |
| `notes`             | string         | optional | shown on the row                                 |

Any other top-level key fails validation. The whitelist keeps the
leaderboard's contract narrow — contributors can't smuggle opaque fields
through.

## Submit flow

`synthbench submit --config <yaml> <run.json>` does three things in order:

1. Loads + validates the YAML. On failure, the validator surfaces every
   error in one pass (no fix-one, re-run, repeat) and exits with code 2.
2. Cross-checks `harness_version` against the installed `synthbench`. A
   mismatch is fatal unless `--allow-harness-mismatch` is passed.
3. Stamps the canonicalised config dict onto the submission body as the
   `user_config` top-level key, then POSTs to the Worker exactly like a
   plain `synthbench submit` would.

The Worker sees a familiar body shape (the existing `config` block is
untouched) plus a new `user_config` field. Leaderboard row identity moves
from `{provider}/{model}` to `{user_config.vendor}/{user_config.config_name}`
when the field is present; rows without `user_config` continue to render
under their vendor default.

### Where it lives in the submission body

```json
{
  "benchmark": "synthbench",
  "schema_version": "...",
  "config": { "...existing provider+dataset config..." },
  "scores": { "...existing scores..." },
  "aggregate": { "..." },
  "per_question": [ "..." ],
  "user_config": {
    "vendor": "synthpanel",
    "vendor_version": "1.4.0",
    "config_name": "wesley-healthcare-northcentral",
    "contributor": "@wesley",
    "harness_version": "0.1.0",
    "target_subgroup": { "description": "...", "selector": { "..." } },
    "packs": [ "healthcare-patient", "general-consumer" ],
    "ensemble_weights": [ 0.7, 0.3 ],
    "extra_prompts": { "system": "..." },
    "decoding": { "temperature": 0.6, "top_p": 0.9 },
    "notes": "..."
  }
}
```

We keep `user_config` at the top level (not inside `config`) so the
existing `config_id` hash, which only reads a fixed set of keys under
`config`, is unaffected. The new row identity is `{vendor}/{config_name}`,
not the underlying provider config.

## Win-region highlight

The leaderboard renders a per-config "win region" — the subset of questions
where the configuration outperforms the vendor's default — by intersecting
the config's `target_subgroup.selector` with the per-question demographic
metadata and re-aggregating. Configs without a `selector` get whole-bench
scoring only.

Leaderboard UI work (row grouping, win-region rendering, the re-run button)
is tracked separately under follow-up beads filed against this one; this
document specifies the on-disk artifact + submission body so the UI work
has a stable schema to build against.

## Reproducibility contract

Each config is a reproducible artifact pinned to:

- the harness version (`harness_version`)
- the vendor adapter version (`vendor_version`)
- the contributor's published prompts and decoding knobs

Anyone with the same harness and an API key for the same vendor can re-run
the benchmark against the config and expect the same scores (modulo
sampling noise). The "Re-run" button on the leaderboard (see follow-up
beads) kicks off a CI verification that does exactly that.

## Sample configs

See [`templates/user-configs/`](../templates/user-configs/) for ready-to-edit
starting points.
