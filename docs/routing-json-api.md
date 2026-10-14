# `routing.json` API

`routing.json` names the best measured system (single model or blend) for
each use case and question topic. Althing reads it to choose a model when a
user asks for `auto` routing. It is built from the same results and the same
dedup as [`leaderboard.json`](leaderboard-json-api.md).

## Endpoint

```
GET https://synthbench.org/data/routing.json
```

- Content type: `application/json; charset=utf-8`
- CORS: `Access-Control-Allow-Origin: *`
- Cache: same policy as `leaderboard.json` (1 hour browser, 6 hours edge,
  24 hours stale-while-revalidate; see `site/public/_headers`)

## Response shape

```jsonc
{
  "api": {
    "name": "synthbench-routing",
    "version": "1.1.0",
    "contract_url": "https://github.com/DataViking-Tech/SynthBench/blob/main/docs/routing-json-api.md"
  },
  "generated_at": "2026-10-14T22:01:42.005155+00:00",
  "taxonomy": {
    "version": 1,
    "topics": [
      {
        "id": "politics",
        "label": "Politics and policy",
        "description": "Elections, parties, government, ...",
        "keywords": ["abortion", "ballot", "congress", "..."]
      }
      // economy, technology, science-health, identity, society, global
    ]
  },
  "slices": [
    { "id": "us-general", "label": "US general public", "datasets": ["opinionsqa", "gss"] },
    { "id": "us-subgroups", "label": "US demographic subgroups", "datasets": ["subpop"] },
    { "id": "cross-national", "label": "Respondents outside the US", "datasets": ["globalopinionqa"] }
  ],
  "min_questions": 30,
  "routes": [
    {
      "slice": "us-general",
      "topic": "all",
      "n_questions": 175,
      "n_by_dataset": { "opinionsqa": 100, "gss": 75 },
      "excluded_for_coverage": 0,
      "confident": true,
      "best": "ensemble--complementary-4--tdefault--tplcurrent--b1126bc8",
      "best_althing": "althing--qwen3.8-flash--tdefault--tplcurrent--b8582ca4",
      "best_single_althing": "althing--qwen3.8-flash--tdefault--tplcurrent--b8582ca4",
      "candidates": [
        {
          "config_id": "ensemble--complementary-4--tdefault--tplcurrent--b1126bc8",
          "label": "Ensemble: Qwen 3.8 Flash (Althing), Sonnet 4 (Althing), DeepSeek V4.1 Flash, Gemini 2.5 Flash-Lite",
          "kind": "blend",
          "althing_native": false,
          "members": [
            { "model_id": "qwen/qwen3.8-flash", "framework": "product", "weight": 0.25 },
            { "model_id": "anthropic/claude-sonnet-4", "framework": "product", "weight": 0.25 },
            { "model_id": "deepseek/deepseek-v4.1-flash", "framework": "raw", "weight": 0.25 },
            { "model_id": "google/gemini-2.5-flash-lite", "framework": "raw", "weight": 0.25 }
          ],
          "index": 57.5,
          "ci": [51.8, 62.5],
          "n": 175,
          "cost_per_100q": null
        }
        // ... up to 12 candidates, sorted by index
      ]
    }
    // one route per (slice, topic) that has questions
  ]
}
```

## Fields

### Taxonomy

Seven topics (taxonomy version 1), defined once in
[`src/synthbench/topics.py`](../src/synthbench/topics.py):

| id | label |
|---|---|
| `politics` | Politics and policy |
| `economy` | Economy and work |
| `technology` | Technology and media |
| `science-health` | Science and health |
| `identity` | Identity and values |
| `society` | Family, community and safety |
| `global` | Global affairs |

Each topic has a `description` and a `keywords` list. Keywords are lowercase
words or phrases. A keyword matches when it appears in the lowercased text on
word boundaries (regex `\b<keyword>\b`, with any run of whitespace between
the words of a phrase). A substring inside a longer word never matches:
"nation" does not match "discrimination". To classify text, count the
keywords of each topic that match; the topic with the most matches wins, ties
go to the topic listed first, and text with no match has no topic.

SynthBench uses the keywords only for questions without a committed label.
Every question in the OpinionsQA, SubPOP, GSS and GlobalOpinionQA pools has
one (`src/synthbench/data/topics/<dataset>.json`):

- OpinionsQA: the dataset's official coarse topic (`topic_mapping.npy`, the
  first `cg` entry), mapped as in the table below. The 13 questions with no
  coarse topic were labeled by the model labeler.
- SubPOP, GSS, GlobalOpinionQA: a model labeler
  ([`scripts/label-topics.py`](../scripts/label-topics.py)), `qwen/qwen3.8-flash`
  at temperature 0, constrained to the seven ids, with four OpinionsQA
  examples per topic. On 300 held-out OpinionsQA questions it agreed with the
  official mapping on 256 (85.3%).

| id | OpinionsQA coarse topics |
|---|---|
| `politics` | political issues; leadership; immigration |
| `economy` | economy and inequality; personal finance; job/career; status in life |
| `technology` | news, social media, data, privacy; corporations, banks, technology and automation |
| `science-health` | science; community health; healthcare system; personal health |
| `identity` | race; gender & sexuality; discrimination; religion; self-perception and values |
| `society` | relationships and family; crime/security; education; future |
| `global` | global attitudes and foreign policy |

OpinionsQA's "community health" topic covers local community life
(neighbors, local problems, urban and rural living), so those questions are
under `science-health`.

### Slices

A slice is a use case: who the study simulates. Each lists the datasets whose
respondents match it. Althing picks the slice from the study's population.

### Routes

One route per (slice, topic) that has at least one question, plus a `topic:
"all"` route per slice.

- `n_questions`: questions in the route, summed over the slice's datasets.
  `n_by_dataset` gives the split.
- `candidates`: the current leaderboard rows (same dedup as `publish-data`),
  singles and ensembles, without baselines and without template, temperature,
  persona-pack, harness or reasoning-effort variants. A candidate must have
  a row on every dataset in the slice and enough question coverage (see
  "Question set and bootstrap"). Sorted by `index`, highest first. At most
  12, and the candidates named by `best_althing` and `best_single_althing`
  are always included.
- `excluded_for_coverage` (since 1.1.0): candidates left out of this route
  because they answered too few of its questions.
- `best`: the top candidate. `best_althing`: the top candidate whose members
  all ran through Althing (`althing_native`). `best_single_althing`: the top
  `althing_native` single. Either can be `null`.
- `confident`: `true` when `n_questions >= min_questions` and the 95%
  interval of (best minus runner-up), from a paired bootstrap, excludes 0.
  Routes with a single candidate are never confident.

### Candidates

- `config_id`: the system's config id without a dataset in the hash (the
  leaderboard's per-dataset `config_id`s include the dataset).
- `kind`: `single` or `blend`.
- `members`: `model_id` is the OpenRouter-style `<vendor>/<model>` slug.
  `framework` is `product` (run through Althing persona conditioning) or
  `raw` (raw prompt). `weight` is the member's share of the blend: the
  weights the ensemble recorded, normalized to sum to 1, or equal weights if
  none were recorded. Singles have one member with weight 1.0.
- `althing_native`: every member is `product`.
- `index`: SynthBench Index on the route's questions. For each dataset in the
  slice, the full SPS (mean of p_dist, p_rank and p_refuse, from per-question
  JSD, Kendall tau and model and human refusal rates) on that dataset's
  questions in the route, rescaled as
  `100 * (SPS - SPS_random) / (ceiling - SPS_random)`. `SPS_random` is the
  random baseline's SPS on the same questions; `ceiling` is the dataset's
  split-half human ceiling (pinned in `synthbench.routing.DATASET_CEILINGS`,
  the same values as `site/src/lib/ceilings.ts`). The route value is the
  question-weighted mean over datasets. 0 is random answers; 100 is the human
  ceiling.
- `ci`: 95% bootstrap interval of `index`.
- `n`: questions the candidate was scored on (equal to `n_questions`).
- `cost_per_100q`: the leaderboard's cost per 100 questions, weighted by the
  route's questions per dataset; `null` when any dataset's cost is unknown.

### Question set and bootstrap

For each dataset, the pool is the random baseline's questions in the topic.
Systems run on different question sets: most have 100 questions per
dataset, and some have the larger `--suite routing` sets (whole OpinionsQA
and GSS pools; SubPOP and GlobalOpinionQA topped up to 75 questions per
topic). A candidate stays in the route only if, on every dataset in the
slice, it answered at least 90% as many pool questions as the best-covered
candidate. The route then uses the pool questions every remaining candidate
answered, so all candidates are scored on the same questions.

Runs on the `--suite routing` sets (stamped `config.suite = "routing"`) are
used here and nowhere else. The leaderboard, findings, run counts and the
Groups page keep using the 100-question runs, so every leaderboard row stays
on the same questions and the random-baseline anchor of the Index does not
move. The bootstrap resamples
questions within each dataset (2,000 resamples, fixed seed per route) and
applies the same draws to every candidate and to the random baseline, so
differences between candidates are paired.

Topic routes on 100-question runs are small, so most of them are not
`confident`. Consumers should fall back to the slice's `all` route when a
topic route is not confident.

## Versioning

`api.version` is semver. Additive changes (new optional fields, new slices,
new topics in a new taxonomy version) bump the minor version. Renamed or
removed fields bump the major version. Consumers must ignore unknown keys.

## Source

Built by `synthbench publish-data --routing-output site/src/data/routing.json`
in CI and in the Pages deploy (or standalone with `synthbench publish-routing`).
The code is [`src/synthbench/routing.py`](../src/synthbench/routing.py); the
endpoint is
[`site/src/pages/data/routing.json.ts`](../site/src/pages/data/routing.json.ts).
