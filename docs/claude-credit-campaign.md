# Claude credit campaign

The November 25, 2026 campaign tests three product decisions: which Claude
models merit routing coverage, whether population conditioning and structured
capture improve fidelity independently, and whether more synthetic samples
reduce error or merely stabilize a biased distribution.

## Collection

`scripts/run-credit-campaign.py` collects individual responses into a private,
append-only JSONL journal. It uses the existing OpenRouter raw prompt and
Althing survey request builders. This is an experimental collection format,
not a leaderboard submission or a measurement of the entire Althing product.

Each task has a unique `id`, `dataset`, `question_key`, explicit OpenRouter
`anthropic/*` model, and `provider` (`openrouter` or `althing`). Optional fields
are `elicitation`, `persona_pack`, `replicate`, `sample_index`, and
`samples_per_question`. Population allocations use the question key and
replicate as their seed; the same allocation is used across capture modes.

Run `--help` for the interface. A no-network preflight is:

```sh
.venv/bin/python scripts/run-credit-campaign.py \
  --tasks .runtime/claude-credit-20261125/pilot-tasks.jsonl \
  --journal .runtime/claude-credit-20261125/pilot.jsonl \
  --questions-dir .runtime/claude-credit-20261125 \
  --pricing .runtime/claude-credit-20261125/openrouter-models.json \
  --max-usd 5 --deadline 2026-11-25T23:15:00Z --dry-run
```

Supply `OPENROUTER_API_KEY` privately through Doppler for actual inference.
Question snapshots contain licensed text and answer keys: keep snapshots,
manifests, and journals in the ignored `.runtime/` directory or private storage.
Only request-side text, options, and respondent population reach the model.
Never commit answer keys or raw campaign journals to this public repository.

## Budget and replay

The funding is a separate Claude promotion on the account's upstream BYOK
credential. A real probe returned `is_byok=true`, gateway `usage.cost=0`, and
positive `cost_details.upstream_inference_cost`. Therefore a zero gateway
charge must never be treated as free inference. The collector accounts the
larger of upstream and gateway charges, without adding the two together;
when billing evidence is unavailable it retains a conservative reservation or
uses an explicitly labeled token-rate estimate.

Reservations are written before dispatch and include outstanding requests.
Lost or failed requests retain their reservation because an absent response
does not prove absence of upstream billing. Final tasks are not dispatched
again. Runtime, pricing, and question-input fingerprints prevent incompatible
replays. A changed collector/runtime requires a new journal and a budget that
subtracts prior spending. Keep a separate campaign-wide total across journals.

To repair an infrastructure failure, create a new task id with `retry_of` set
to the failed task id. Preserve its configuration, question, replicate, sample
index, and sample count. Keep the original manifest and journal unchanged and
pass all original and repair manifests/journals to the analyzer. Retry chains
must be linear, and every parent must have an observed final `error` record.
A completed answer, model refusal, or parse failure cannot be retried this way.
The terminal retry fills one logical sample slot; ancestor errors, charges,
and explicit recovery history remain in the analysis. Apply a separate repair
budget and include it in the campaign-wide total.

The request reserve uses UTF-8 bytes, framing allowance, output ceilings, and
a cache-write premium. This is a conservative estimate, not a formal provider
token-count guarantee. An observed overrun stops collection for reconciliation.
Althing's internal retries are disabled; raw adapter recovery attempts are
reserved and recorded individually. These retry settings are part of the
campaign's provenance.

## Frozen experiment

Initial spending ceilings are $5 pilot, $60 model screening, $80 population
and capture, and $35 sample-size analysis, with $20 held for useful extensions.
Stop new requests at the frozen deadline, conservatively before credit expiry.
The deadline governs admission, not completion: allow at least three minutes
for in-flight calls and billing reconciliation before the actual expiry.

- Screening: Haiku 5.5, Sonnet 5.5, and Opus 5.5; raw and Althing; four core
  datasets; 50 questions and 20 samples per cell. Extend promising candidates
  only after measuring actual cost and throughput.
- Population and capture: Haiku 5.5 and Sonnet 4.6; generic and global-respondents;
  natural and structured; 60 matched GlobalOpinionQA questions, 30 samples,
  and three independent repetitions. Freeze roughly two thirds development
  and one third evaluation before inspecting outputs. Assign by normalized
  question-text hash, keeping identical items in the same split across datasets.
- Sample size: two configurations, 60 questions, up to 150 samples. Analyze
  nested prefixes at 10, 20, 30, 60, 100, and 150 responses.

The pilot found that Sonnet 5.5 rejects forced tool capture (`tool_choice`
types `tool` and `any`) with HTTP 400. It stays in natural model screening;
Sonnet 4.6 replaces it only in the matched capture experiment. Do not silently
change structured capture to optional tool use: that would change the
experimental condition. All eight Haiku 5.5/Sonnet 4.6 population and capture
combinations passed the revised connectivity pilot.

Althing's Messages passthrough returns an Anthropic `msg_*` body id and an
OpenRouter `gen-*` header. The per-instance instrumentation in
`campaign_transport.py` preserves both ids and raw usage without changing
native request bodies, provider routing, decoding parameters, or parsing.
The generation header is required for successful OpenRouter billing lookup;
an Anthropic message id cannot be looked up as an OpenRouter generation.

Prefer questions absent from committed result artifacts. The available
GlobalOpinionQA and SubPOP pools contain such items; the available OpinionsQA
and GSS pools do not. Label the latter as replications. Absence from local
results does not establish absence from model training.

The restored SubPOP snapshot is a population-average distribution, not a
conditioned demographic benchmark. Its screening result cannot establish
subgroup fidelity. Country-level conclusions likewise need sufficient
country-specific samples. Report paired question-level uncertainty, keep
development and evaluation results separate, and never count synthetic
respondents as independent human observations. Publish only validated,
complete and comparable configurations through the normal submission flow.

The analysis reports unscored-cell counts alongside its means. It deliberately
declines paired contrasts when either side has unscorable cells; dropping
questions a model refused entirely could make that model appear better.
All-refusal or all-unparseable cells have no distributional score rather than
receiving the runner's historical uniform fallback. These experimental means
are conditional on scorable cells and must not be presented as leaderboard SPS.

## Adapter change

OpenRouter now omits temperature when the caller omits it, preserving explicit
values including zero. Historical absent-temperature raw runs actually sent
1.0; new absent-temperature runs use the upstream default. Both retain the
existing `tdefault` identity, so campaign comparisons must use the recorded
runtime and request evidence rather than silently pooling old and new runs.
