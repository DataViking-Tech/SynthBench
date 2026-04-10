# SynthBench

Open benchmark harness for synthetic survey respondent quality.

**The MLPerf of synthetic UXR.**

SynthBench measures how well synthetic respondent systems (like [synth-panel](https://github.com/DataViking-Tech/synth-panel), Ditto, Synthetic Users, or raw ChatGPT prompting) reproduce real human survey response patterns.

## Leaderboard

**[View the live leaderboard](https://dataviking-tech.github.io/synthbench/)**

Regenerate from results:
```bash
synthbench publish --results-dir ./leaderboard-results --output docs/
```

## Status

Phase 1 complete: OpinionsQA evaluation harness with CLI, multiple providers, and public leaderboard.

## Ground Truth

Built on established academic datasets:
- [OpinionsQA](https://github.com/tatsu-lab/opinions_qa) (Santurkar et al., ICML 2023) — 1,498 questions from Pew American Trends Panel
- [GlobalOpinionQA](https://arxiv.org/abs/2306.16388) (Durmus et al., 2024) — cross-national opinion data

## License

MIT
