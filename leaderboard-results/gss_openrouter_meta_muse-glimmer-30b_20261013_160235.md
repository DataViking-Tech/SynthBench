# SynthBench Score Card

**Provider:** openrouter/meta/muse-glimmer-30b
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 454.5s

## SynthBench Parity Score (SPS)

**SPS: 0.5438 [0.5156, 0.5785]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.3192 [0.2707, 0.3771] | ███░░░░░░░ |
| P_rank  Rank-Order | 0.3413 [0.2978, 0.3922] | ███░░░░░░░ |
| P_refuse Refusal Cal. | 0.9708 [0.9626, 0.9760] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.6808 |
| Median JSD | 0.7384 |
| Mean Kendall's tau | -0.3174 |
| Composite Parity (legacy) | 0.3302 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.2317 | -41% |
| random-baseline | 0.6495 | -0.3193 | -49% |

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
| Please tell me whether or not you think it should be possibl... | 0.0608 | 0.3333 |
| Tell me if you agree or disagree with this statement: Most m... | 0.1008 | 0.3333 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1233 | 0.8165 |
| Consider a man who admits he is a Communist. Suppose this ad... | 0.2194 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If you were asked to use one of four names for your social c... | 0.9565 | -0.6325 |
| Which of these statements comes closest to your feelings abo... | 0.9629 | -0.7071 |
| What is your opinion about a married person having sexual re... | 0.9660 | -0.6325 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| I am going to name an institution in this country. As far as... | 0.9714 | -0.7071 |
