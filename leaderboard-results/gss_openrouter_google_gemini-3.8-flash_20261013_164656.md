# SynthBench Score Card

**Provider:** openrouter/google/gemini-3.8-flash
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 1146.9s

## SynthBench Parity Score (SPS)

**SPS: 0.5311 [0.4985, 0.5700]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.2903 [0.2369, 0.3491] | ███░░░░░░░ |
| P_rank  Rank-Order | 0.3309 [0.2769, 0.3915] | ███░░░░░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.7097 |
| Median JSD | 0.8116 |
| Mean Kendall's tau | -0.3382 |
| Composite Parity (legacy) | 0.3106 |

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
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1233 | 0.8165 |
| Suppose there is a community-wide vote on the general housin... | 0.1280 | 0.7071 |
| Tell me if you agree or disagree with this statement: Most m... | 0.1379 | 0.8165 |
| Consider a man who admits he is a Communist. Suppose this ad... | 0.2194 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In general, do you find life exciting, pretty routine, or du... | 0.9684 | -0.7071 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| We are interested in how people are getting along financiall... | 0.9806 | -0.7071 |
| Taken all together, how would you say things are these days-... | 0.9826 | -0.7071 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
