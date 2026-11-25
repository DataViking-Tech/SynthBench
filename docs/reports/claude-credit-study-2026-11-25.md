# Claude credit study: complete capture, qualified conclusions

**121,200 logical responses completed. Neither independent confirmation gate
was established under the frozen analysis rules.** The campaign produced
useful software fixes and a reproducible dataset without changing model
defaults or claiming human behavioral validity.

The [frozen confirmation protocol](../claude-population-confirmation-2026-11-25.md)
was pushed before inference. The [sanitized aggregate artifact](data/claude-credit-study-2026-11-25.json)
contains coverage, accounting, exploratory effects and the withheld gate
records. Licensed questions, human distributions and individual model outputs
remain private.

## What ran

| Phase | Design | Completed slots | Complete / scorable cells |
| --- | --- | ---: | ---: |
| Exploratory | Four-dataset Claude screen; population/capture factorial; sample prefixes | 85,200 | 2,760 / 2,747 |
| Independent confirmation | 300 additional GlobalOpinionQA questions, four natural-capture arms, 30 responses per arm | 36,000 | 1,200 / 1,197 |

All 114 infrastructure-error slots were recovered with explicit retry
lineage. Original errors and spending remain in the journals. Completed
refusals and parse failures were not retried. The separate connectivity pilots
are excluded from these logical-response counts.

The confirmation draft changed from 100 questions with three replicates to
300 questions with one replicate before any confirmation inference. Models,
30-response panel size, primary gates, three-point margin and spending caps
were preserved. The original draft remains archived. Broader question
coverage addressed the dominant exploratory variance at the same 36,000
responses.

## Exploratory findings

- On 21 held-out GlobalOpinionQA questions with three replicates averaged per
  question, Sonnet 4.6 natural population conditioning increased conditional
  composite parity by **6.86 points**, paired 95% BCa interval **3.56–11.47**.
  These exploratory intervals were not adjusted for multiple comparisons.
- Structured capture had zero parse failures in the four exploratory
  structured arms. It did not establish a positive parity effect; one Haiku
  population-conditioned comparison showed lower distributional parity.
  Structured capture is a format option, not an established fidelity upgrade.
- Increasing generic natural panels from 10 to 150 samples did not establish
  an evaluation composite-parity improvement on the 21-question subset.
  The full 10/20/30/60/100/150 prefixes are preserved. This does not establish
  a universal sample-size optimum.
- Raw and Althing request paths differed substantially, and some raw cells
  had no valid answers. Model names alone are insufficient configuration
  identities; provider, population context, capture and parser version matter.

These are historical survey-distribution measurements. Calls and synthetic
personas are not independent human respondents. The SubPOP screen used its
population-average target; it did not validate conditioned subgroups.

## Confirmation result: not established

Both primary gates required complete, scorable coverage of every selected
question in both compared configurations:

1. Sonnet 4.6 population-conditioned minus generic distributional parity
   (`P_dist`) had to have a paired interval lower endpoint above zero.
2. Haiku population-conditioned minus Sonnet population-conditioned `P_dist`
   had to have a lower endpoint above the predeclared **−0.03** margin.

The frozen method used paired question-level BCa intervals, 5,000 resamples,
seed 42, and two directional tests with one-sided alpha 0.025 each. This gives
nominal Bonferroni familywise control; bootstrap coverage is approximate.

Three completed cells had no valid selections. They affected a generic Haiku
arm and both Sonnet arms, so the strict analyzer withheld both primary
contrasts. **No primary interval was reported and no gate passed.** This is
not a statistical finding of inferiority or absence of population benefit.
No questions were dropped, outcomes imputed, margins relaxed, or completed
nonanswers rerun to obtain a result.

An audit found missing instrument context in two source items: a conditional
multipart item and unresolved country-specific group context. The models
returned nonempty responses but did not select an offered answer in the
three blocking cells. A parser cannot legitimately invent those votes.
Instrument auditing is tracked in [#405](https://github.com/DataViking-Tech/SynthBench/issues/405).

For transparency, these are **descriptive means conditional on each arm's
scorable cells**. Their denominators differ, so this table cannot establish
either withheld paired gate or a model ranking:

| Natural-capture configuration | Completed responses | Scorable questions | Conditional `P_dist` | Accounted USD (rounded) |
| --- | ---: | ---: | ---: | ---: |
| Haiku 5.5, generic | 9,000 | 299 / 300 | 0.6215 | 1.00 |
| Haiku 5.5, population | 9,000 | 300 / 300 | 0.7356 | 1.24 |
| Sonnet 4.6, generic | 9,000 | 299 / 300 | 0.5906 | 18.24 |
| Sonnet 4.6, population | 9,000 | 299 / 300 | 0.7246 | 24.76 |

The Haiku population arm used approximately **5.02%** of the Sonnet
population arm's accounted spending for the same completed response count.
The study did not qualify a cheaper preset as distributionally noninferior.
Conditional composite means are also not leaderboard SPS or evidence that
synthetic respondents reproduce real-world behavior.

## Product decisions and ordinary reruns

Keep current defaults and auto-routing. Population-pack variants are
intentionally excluded from `routing.json`, and this study does not qualify
them for automatic selection. Use the population-aware configuration only as
an explicit research option with a source-supported respondent population.

For an ordinary SynthBench rerun with Althing 1.9.1 or a compatible version:

```sh
synthbench run --provider althing \
  --model openrouter/anthropic/claude-haiku-5.5 \
  --dataset globalopinionqa --persona-pack global-respondents \
  --elicitation natural --samples 30 --n 28 \
  --output results/global-population-research/
```

Use `openrouter/anthropic/claude-sonnet-4.6` for the Sonnet comparator.
This recipe is not exact campaign replay: its question set and population
allocation seed differ. Exact replay uses the frozen manifests and snapshots
with `scripts/run-credit-campaign.py`; model sampling remains stochastic.
User-configuration YAML is submission metadata, not a `run` preset loader.
Althing's standalone `--population` filters a persona pack and does not
reproduce this benchmark's 30-response country allocation.

Treat structured capture as opt-in for format requirements. Sonnet 5.5
rejected forced tool capture in the pilot; Sonnet 4.6 was used for the matched
capture experiment. Do not silently substitute optional tool use for forced
capture.

## Accounting and software outcome

Known ledgers and the separate successful probe account for **$166.334541455**.
This includes retained reservations and estimates, not solely proven debits.
Reserving the full $5 pilot/probe envelope instead gives **$171.284450805**,
leaving **$28.715549195** of the $200 authorization unused. The upstream
promotional balance was not independently queried.

OpenRouter BYOK responses can report zero gateway cost while consuming
upstream Claude credits. The campaign accounts the larger per-attempt
gateway/upstream value without adding overlapping measures. Lost or failed
requests retain conservative reservations. Both private archives have local
SHA-256 digests and matching remote HEAD size/SHA metadata; remote bytes were
not read back.

The work merged request-temperature fidelity, response-level spending and
replay controls, native generation/billing evidence, and strict retry analysis
in [#403](https://github.com/DataViking-Tech/SynthBench/pull/403) and
[#404](https://github.com/DataViking-Tech/SynthBench/pull/404). Sol and Opus
council reviews covered actual code changes, and required CI passed.

The audit also identified a separate first-line parser false positive: prose
mentioning several offered options could be converted to a vote. Parser
hardening is a prospective software correction. **All study results above
retain frozen parser version 3; the original journals and analyses are not
reclassified as a successful confirmation.**
