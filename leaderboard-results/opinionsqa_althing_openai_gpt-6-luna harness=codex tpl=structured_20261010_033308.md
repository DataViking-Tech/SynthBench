# SynthBench Score Card

**Provider:** althing/openai/gpt-6-luna harness=codex tpl=structured
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2062.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8156 [0.7930, 0.8361]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7283 [0.6901, 0.7577] | ███████░░░ |
| P_rank  Rank-Order | 0.7243 [0.6870, 0.7583] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2717 |
| Median JSD | 0.2426 |
| Mean Kendall's tau | 0.4486 |
| Composite Parity (legacy) | 0.7263 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1643 | +29% |
| random-baseline | 0.6495 | +0.0768 | +12% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Temporal Breakdown (by Survey Year)

Scores stratified by Pew ATP survey wave year. Rising P_dist in recent years may indicate training-data contamination.

| Year | P_dist | P_rank | Mean JSD | Questions |
|------|--------|--------|----------|-----------|
| 2017 | 0.7278 | 0.7255 | 0.2722 | 99 |
| 2018 | 0.7790 | 0.6118 | 0.2210 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0103 | 0.8165 |
| How well, if at all, do the following words or phrases descr... | 0.0147 | 0.7746 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Do you feel that society in general tends to look at most gu... | 0.0291 | 1.0000 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Does anyone else in your household own any guns (not includi... | 0.6009 | -0.3333 |
| Do you personally own any guns (not including air guns, such... | 0.6897 | -0.3333 |
| Regardless of whether or not you own a gun, have you ever fi... | 0.7116 | -1.0000 |
| Do you think men and women are basically similar or basicall... | 0.7490 | 0.0000 |
| Thinking about when you were growing up, as far as you know,... | 0.8239 | -0.2357 |
