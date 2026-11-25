# Claude population confirmation: frozen protocol

Protocol version 2 was frozen at **2026-11-25 16:48:44 UTC**, before any
confirmation inference. This follows the exploratory
[Claude credit campaign](claude-credit-campaign.md). Results belong in a
separate report; this file records the decisions made before collection.

## Question and fixed design

Does matching the survey's respondent population improve distributional
fidelity, and can an inexpensive population-conditioned model preserve
distributional fidelity within a useful tolerance?

The design has 300 additional GlobalOpinionQA questions, four configurations,
and 30 responses per question/configuration: **36,000 planned responses**.

| Model | Respondent context | Capture |
| --- | --- | --- |
| `anthropic/claude-haiku-5.5` | Generic | Natural |
| `anthropic/claude-haiku-5.5` | `global-respondents` | Natural |
| `anthropic/claude-sonnet-4.6` | Generic | Natural |
| `anthropic/claude-sonnet-4.6` | `global-respondents` | Natural |

All calls use the same Althing survey adapter and OpenRouter Messages
transport as the exploratory campaign. There is one replicate (`replicate=0`)
per question/configuration. Population allocations use the same question seed
across models. Models receive no human distributions, previous answers,
benchmark scores, or study hypotheses.

The private version-1 draft proposed 100 questions with three replicates.
It is preserved verbatim and superseded before inference. Exploratory
variance analysis found question variation dominant; 300 questions with one
replicate provide more precision at the same response count and spending cap.
Planning power estimates are approximate and are not guarantees. This design
tests average performance across questions and the sampling design, not
within-question repeatability.

## Question selection

Normalize text by case-folding, replacing non-word runs with spaces, and
stripping surrounding spaces. Exclude committed GlobalOpinionQA result keys
and normalized text, the original campaign's 80 reserved GlobalOpinionQA
keys, and reserved normalized text from every original dataset. Retain
questions with available canonical human distributions.

Sort candidates by `(SHA256("claude-confirmation-20261125-v1:" +
normalized_text), question_key)` and take the first 300 distinct normalized
texts. Selection never uses answer values or model outputs. All selected
questions are confirmation evaluation questions; no tuning split is used.
Absence from prior campaign artifacts does not establish absence from model
training. The surveys are historical, not current behavioral ground truth.

## Two directional primary gates

1. **Population gain:** Sonnet 4.6 population-conditioned minus generic
   `P_dist` has a paired confidence-interval lower bound greater than zero.
2. **Distributional noninferiority:** Haiku population-conditioned minus
   Sonnet population-conditioned `P_dist` has a lower bound greater than
   **−0.03**. Three distributional-parity points is a predeclared product
   tolerance for a materially cheaper option, not an equivalence claim.

Use paired question-level BCa bootstrap intervals, 5,000 resamples, seed 42.
Each gate uses the lower endpoint of its two-sided 95% interval: a one-sided
alpha of 0.025 for each of two tests, with nominal Bonferroni familywise
control at 0.05. Bootstrap coverage is approximate. Both gates must pass to
recommend a cheaper population-conditioned preset on this evidence.

Conditional composite parity, rank parity, refusal, parsing, cost, latency,
and the Haiku population effect are exploratory secondary outcomes.
Distributional noninferiority does not establish composite-score equivalence,
human behavioral validity, or country-specific fidelity. These experimental
conditional metrics are not leaderboard SPS.

Incomplete or unscorable cells remain explicit. The analyzer declines a
primary contrast if either configuration has an unscorable cell; questions
will not be dropped to obtain a favorable estimate. Completed refusals and
parse failures are not retried. Infrastructure errors may receive explicit
linear repairs with their full history and charges preserved.

## Budget and immutable evidence

Collection is capped at **$65**, aggregate repairs at **$3**, with at most two
repair rounds. Stop admitting requests at **23:15 UTC**, with completion
margin before the promotion expires. Counting the original campaign's
$121.038759055 ledger and the full $5 pilot envelope, these ceilings total
**$194.038759055**, below the $200 authorization.

Hashes below are SHA-256 over exact file bytes, not JSON reserialization:

| Private artifact | SHA-256 |
| --- | --- |
| `confirmation/confirmation-tasks.jsonl` | `1a30e671fdc4d0d2a16396b7836d51d15b5ad4da7fd2e1a8b239a4295bde5e4c` |
| `confirmation/confirmation-selection.json` | `a3347eeb4b686c77e2e310933cd366ff410bd25c16590c8268256a39325009dd` |
| `globalopinionqa-questions-private.json` | `5b2f8f22afaa0793d629b1fec13e90a43d0ff343842c289468c6b55d306e1751` |
| `openrouter-models.json` | `5abd56aa5ac85865460bce1a7357dabbd676c2ae2b3df2d106ff2359ed8e5609` |

Licensed snapshots, individual responses, manifests, both protocol versions,
and billing journals remain private. This confirmation does not change
Althing defaults or auto-routing. Population-pack configurations are currently
excluded from the routing API; any recommendation must be explicitly opt-in.
