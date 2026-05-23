# Leaderboard JSON API

Stable HTTP endpoint for downstream consumers (SynthPanel `--best-model-for`,
agents, dashboards) that want SynthBench's current model recommendation data
without scraping the site or cloning the repo.

Issue: [#295](https://github.com/DataViking-Tech/SynthBench/issues/295) · Bead: sb-ty6

## Endpoint

```
GET https://synthbench.org/data/leaderboard.json
```

Returns `application/json; charset=utf-8`. CORS is `*` so browser-side
consumers can fetch directly.

## Response shape

```jsonc
{
  "api": {
    "version": "1.0.0",
    "contract_url": "https://github.com/DataViking-Tech/SynthBench/blob/main/docs/leaderboard-json-api.md"
  },
  "generated_at": "2026-04-15T02:09:01.677545+00:00",
  "synthbench_version": "0.1.0",
  "datasets": ["globalopinionqa", "opinionsqa", "subpop"],
  "entries": [
    {
      "rank": 1,
      "config_id": "synthpanel--claude-sonnet-4--tdefault--tplcurrent--d1dd307b",
      "provider": "SynthPanel (Sonnet 4)",
      "model": "SynthPanel (Sonnet 4)",
      "dataset": "globalopinionqa",
      "framework": "product",
      "sps": 0.7966,
      "p_dist": 0.9101,
      "p_rank": 0.5,
      "p_refuse": 0.9797,
      "jsd": 0.0899,
      "tau": 0.0,
      "n": 100,
      "ci_lower": 0.6971,
      "ci_upper": 0.7122,
      "is_baseline": false,
      "is_ensemble": false,
      "samples_per_question": 30,
      "topic_scores": { "Economy & Work": 0.6965, "Politics & Governance": 0.7176 },
      "cost_usd": 0.42,
      "cost_per_100q": 1.4,
      "cost_per_sps_point": 0.53,
      "input_tokens": 124000,
      "output_tokens": 18000
      // ...additional optional fields, see types/leaderboard.ts
    }
  ],
  "convergence": [ /* ... */ ],
  "findings": { /* ... */ },
  "baselines": { /* ... */ },
  "pricing_snapshot": { /* ... */ }
}
```

Full TypeScript definition: [`site/src/types/leaderboard.ts`](../site/src/types/leaderboard.ts)

### Required entry fields

Always present on every row:

| Field | Type | Meaning |
| --- | --- | --- |
| `rank` | int | Position in the leaderboard for `(model, dataset)`. |
| `provider` | string | Display name of the system under test. |
| `model` | string | Concrete model identity (often equal to `provider`). |
| `dataset` | string | One of the `datasets` array above. |
| `framework` | string | `product`, `raw`, `synthpanel`, ... |
| `sps` | float | Synthetic Population Similarity score, [0, 1]. |
| `p_dist` / `p_rank` / `p_refuse` | float | SPS sub-metrics. |
| `jsd` | float | Jensen–Shannon divergence to human distribution. |
| `n` | int | Number of questions evaluated. |
| `ci_lower` / `ci_upper` | float | Bootstrap CI on `sps`. |
| `is_baseline` / `is_ensemble` | bool | Row category flags. |

### Optional entry fields

Present when the underlying data supports them. Consumers MUST treat absence as
"unknown" — never zero/default.

`config_id`, `samples_per_question`, `temperature`, `template`,
`normalized_sps`, `p_cond`, `p_sub`, `run_count`, `dataset_coverage_count`,
`cost_usd`, `cost_per_100q`, `cost_per_sps_point`, `is_cost_estimated`,
`input_tokens`, `output_tokens`, `cost_per_response`, `tokens_per_response`,
`latency_p50_seconds`, `latency_p95_seconds`, `topic_scores`,
`topic_metrics`, `demographic_scores`, `replicates`, `sps_public`,
`sps_private`, `sps_public_private_delta`, `verification_badge`,
`sps_held_out`, `sps_held_out_delta`, `held_out_last_run`, ...

## Stability contract

- `api.version` is **semver**.
  - **Major** bump → renamed or removed documented field. Pin and test.
  - **Minor** bump → new optional field, new entries, new datasets. Safe.
  - **Patch** bump → data refresh, no schema change.
- The exact URL `https://synthbench.org/data/leaderboard.json` is part of the
  contract. It will not move or be renamed — only its payload schema is
  versioned. SynthPanel's `sy-nkh` fallback depends on this stability.
- **Forward compatibility**: Consumers MUST tolerate unknown top-level keys
  and unknown `entries[].*` fields. We add fields freely at any minor.
- **Backward compatibility**: Once a field is documented as required, it stays
  required for the lifetime of the current major. Optional fields may flip to
  missing without notice.

## Cache & freshness

| Layer | TTL |
| --- | --- |
| Browser (`max-age`) | 1 hour |
| CF edge (`s-maxage`) | 6 hours |
| `stale-while-revalidate` | 24 hours |

Republished on every push to `main` that changes `leaderboard-results/`,
`src/synthbench/publish.py`, or `site/**` via
[`.github/workflows/cf-pages.yml`](../.github/workflows/cf-pages.yml).
Read `generated_at` from the response body for freshness — do not rely on
HTTP `Date` or `Last-Modified`.

## Consumer guidance

### SynthPanel

```python
import urllib.request, json

resp = urllib.request.urlopen(
    "https://synthbench.org/data/leaderboard.json", timeout=10
)
data = json.loads(resp.read())
entries = data["entries"]
# Filter to your dataset of interest, sort by sps, pick top-k.
```

On HTTP error (any non-200), fall back to a bundled snapshot. SynthBench
guarantees the URL stays reachable, but the network might not.

### Dashboards / agents

The response is large (currently ~hundreds of KB). If you only need
recommendations, project down to `entries[*].{provider, model, dataset, sps,
cost_per_100q, config_id}` before storing. The full payload is rich enough to
reproduce every metric on the public leaderboard.

## Source

Generated at site-build time from `site/src/data/leaderboard.json` (in turn
produced by `synthbench publish-data --results-dir leaderboard-results
--output site/src/data/leaderboard.json` in the CF Pages workflow). The
endpoint route is [`site/src/pages/data/leaderboard.json.ts`](../site/src/pages/data/leaderboard.json.ts).
