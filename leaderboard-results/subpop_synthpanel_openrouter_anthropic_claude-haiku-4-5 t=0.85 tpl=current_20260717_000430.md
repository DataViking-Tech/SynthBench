# SynthBench Score Card

**Provider:** synthpanel/openrouter/anthropic/claude-haiku-4-5 t=0.85 tpl=current
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 96.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7711 [0.7447, 0.7933]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6830 [0.6485, 0.7163] | ███████░░░ |
| P_rank  Rank-Order | 0.6502 [0.5984, 0.6925] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3170 |
| Median JSD | 0.2924 |
| Mean Kendall's tau | 0.3005 |
| Composite Parity (legacy) | 0.6666 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1047 | +19% |
| random-baseline | 0.6495 | +0.0171 | +3% |

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
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| Over the next 20 years, how much impact do you think the use... | 0.0185 | 0.5270 |
| Do you think abortion should be legal or illegal in the situ... | 0.0670 | 0.6667 |
| Do you think whether a relative attended the school should b... | 0.0729 | 0.6667 |
| Do you think abortion should be legal or illegal in the situ... | 0.0753 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How important is your religion in shaping your views about a... | 0.5848 | 0.0000 |
| Thinking about policies around abortion in this country, in ... | 0.6930 | 0.1155 |
| Do you personally know someone (such as a close friend, fami... | 0.7727 | -1.0000 |
| In the news you are receiving about the Biden administration... | 0.9102 | -0.8165 |
| Please choose the statement that comes closer to your own vi... | 0.9582 | -0.8165 |
