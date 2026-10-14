# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-4.5 t=0.85 tpl=demo
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 363.8s

## SynthBench Parity Score (SPS)

**SPS: 0.6675 [0.6364, 0.6968]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6668 [0.6247, 0.7027] | ███████░░░ |
| P_rank  Rank-Order | 0.6375 [0.5903, 0.6765] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.6982 [0.6344, 0.7574] | ███████░░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3332 |
| Median JSD | 0.2830 |
| Mean Kendall's tau | 0.2749 |
| Composite Parity (legacy) | 0.6521 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0901 | +16% |
| random-baseline | 0.6495 | +0.0026 | +0% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think there are situations when abortion should be le... | 0.0282 | 1.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.0345 | 0.4472 |
| Did you refuse to answer the previous question?... | 0.0347 | 1.0000 |
| Do you think whether a relative attended the school should b... | 0.0347 | 0.9129 |
| If an abortion was carried out in a situation where it was i... | 0.0368 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Here’s a list of activities some people do and others do not... | 0.7076 | -0.3333 |
| Please indicate if you have traveled more than 100 miles fro... | 0.7183 | -0.3333 |
| Please indicate if you have attended a concert over the past... | 0.7446 | -0.3333 |
| Have your personal views about abortion changed in any way o... | 0.7775 | -0.1826 |
| Which statement comes closer to your view, even if neither i... | 0.8580 | -1.0000 |
