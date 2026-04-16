# Contributing to SynthBench

Thanks for your interest in contributing. This guide is designed for external
contributors and focuses on the most common contribution paths.

## Ways to contribute

- **Bug fixes** in the benchmark harness (`src/synthbench/`).
- **New providers** or provider improvements (`src/synthbench/providers/`).
- **Dataset and suite updates** (`src/synthbench/datasets/`, `src/synthbench/suites/`).
- **Validation and metric improvements** (`src/synthbench/validation.py`, `src/synthbench/metrics/`).
- **Documentation and examples** (`README.md`, `METHODOLOGY.md`, `SUBMISSIONS.md`, notebooks).

If you're unsure where to start, open an issue describing your proposal.

## Development setup

```bash
git clone https://github.com/DataViking-Tech/synthbench.git
cd synthbench
pip install -e .[dev]
```

Enable local git hooks (recommended):

```bash
./scripts/install-hooks.sh
```

## Typical contributor workflow

1. Create a branch from `main`.
2. Make focused changes (one logical change per PR when possible).
3. Run relevant checks locally.
4. Open a PR with clear context and rationale.

## Local checks

Run what is relevant to your change:

```bash
pytest -q
ruff check .
ruff format --check .
```

For docs-only changes, lightweight checks are fine (e.g., link/path sanity and
format consistency).

## Submitting benchmark results

If your goal is leaderboard participation (rather than code changes), use one
of the submission paths in [`SUBMISSIONS.md`](SUBMISSIONS.md):

- Web upload
- CLI submit with API key
- GitHub PR with result files

## PR expectations

Please include:

- **What changed** and **why**.
- Any tradeoffs, compatibility notes, or follow-up work.
- Evidence that relevant checks were run.

Keep PRs reviewable: smaller and focused beats large and mixed.

## Documentation structure (quick map)

- `README.md` — project entry point and quick start.
- `CONTRIBUTING.md` — contributor workflow and expectations.
- `SUBMISSIONS.md` — leaderboard submission contract and validator rules.
- `METHODOLOGY.md` / `FINDINGS.md` — benchmark framing and experimental results.
- `DATABASE-MIGRATIONS.md` / `supabase/README.md` — maintainer-oriented DB migration notes.
