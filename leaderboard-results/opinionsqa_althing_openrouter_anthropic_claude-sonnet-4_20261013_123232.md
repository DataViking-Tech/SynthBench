# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-sonnet-4
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 640.5s

## SynthBench Parity Score (SPS)

**SPS: 0.8413 [0.8230, 0.8578]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7315 [0.7023, 0.7620] | ███████░░░ |
| P_rank  Rank-Order | 0.7982 [0.7681, 0.8238] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2685 |
| Median JSD | 0.2611 |
| Mean Kendall's tau | 0.5965 |
| Composite Parity (legacy) | 0.7648 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2029 | +36% |
| random-baseline | 0.6495 | +0.1153 | +18% |

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
| 2017 | 0.7331 | 0.7996 | 0.2669 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0158 | 1.0000 |
| Have you participated in any of these groups during the last... | 0.0171 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How well, if at all, do the following words or phrases descr... | 0.5362 | 0.3162 |
| How often, if ever, do you watch TV programs about guns or w... | 0.5375 | 0.3162 |
| In the last 12 months, how often did you and your neighbors ... | 0.5608 | 0.3563 |
| How worried are you right now about not having enough to pay... | 0.5640 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
