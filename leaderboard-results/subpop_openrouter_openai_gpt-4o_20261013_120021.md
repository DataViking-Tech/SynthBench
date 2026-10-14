# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 347.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7633 [0.7341, 0.7843]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6629 [0.6273, 0.6963] | ███████░░░ |
| P_rank  Rank-Order | 0.6469 [0.6041, 0.6848] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3371 |
| Median JSD | 0.3080 |
| Mean Kendall's tau | 0.2939 |
| Composite Parity (legacy) | 0.6549 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0929 | +17% |
| random-baseline | 0.6495 | +0.0054 | +1% |

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
| Do you think artificial intelligence (AI) would do better, w... | 0.0362 | 0.8000 |
| Do you think artificial intelligence (AI) would do better, w... | 0.0402 | 0.8000 |
| Do you think gender should be a major factor, minor factor, ... | 0.0652 | 0.9129 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.0747 | 0.0000 |
| Do you think whether a relative attended the school should b... | 0.0769 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the use of artificial intelligence (AI) in th... | 0.6221 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| Please indicate if you have attended a sporting event over t... | 0.6890 | -0.3333 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.7021 | -0.1826 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
