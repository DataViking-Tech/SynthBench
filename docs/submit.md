# Vendor self-submission via `synthbench submit-adapter`

> **Status: scaffold (refs [#256](https://github.com/DataViking-Tech/SynthBench/issues/256)).**
> The CLI surface and adapter contract are stable. The full evaluation
> pipeline that turns an adapter into a leaderboard-ready submission is
> tracked in follow-up issues.

This is the path SynthPanel competitors take to land on the SynthBench
leaderboard without filing a bespoke evaluation pipeline. The three steps
are: write an adapter, run `synthbench submit-adapter`, open a PR.

## 1. Write an adapter

Subclass `synthbench.adapter.Adapter` in a Python module in your repo:

```python
# my_adapter.py
from synthbench.adapter import Adapter


class MyAdapter(Adapter):
    @property
    def name(self) -> str:
        return "acme-ai/synth-v2"

    @property
    def version(self) -> str:
        return "2026.05.14"

    async def respond(self, *, question, persona, context=None) -> str:
        # Call your model however you want — the harness only cares about
        # the returned string. Pull credentials from the env var you
        # declared via --api-env-var.
        ...
        return "yes"
```

Constraints:

- The adapter must be constructible with no arguments.
- `respond` is called concurrently across questions; keep per-instance
  state asyncio-safe.
- SynthBench never reads your API key. It only checks that the env var
  you name is present.

## 2. Run `synthbench submit-adapter`

```sh
export ACME_API_KEY=...
synthbench submit-adapter \
    --adapter ./my_adapter.py \
    --vendor acme-ai \
    --vendor-version 2026.05.14 \
    --api-env-var ACME_API_KEY \
    --suite core \
    --output-dir ./submission/
```

Exit codes:

| Code | Meaning                                                                 |
| ---- | ----------------------------------------------------------------------- |
| 0    | Submission artifacts written to `--output-dir`.                         |
| 2    | Bad arguments (adapter not importable, wrong shape, etc.).              |
| 3    | API env var not set.                                                    |
| 1    | Runtime failure during evaluation (full pipeline only — not scaffold).  |

## 3. Open the leaderboard PR

`submit-adapter` prints the target URL and a stubbed verification curl.
Once the eval pipeline lands, the contents of `submission.md` will be the
PR body and CI will validate the run-hash reproducibility on merge.

## Worked example: `RandomAdapter`

SynthBench ships a `RandomAdapter` in `synthbench.adapter` for wiring-up
checks. It emits trivial answers and is not a real baseline, but it lets
you confirm your environment can hit the submit path end-to-end:

```sh
export FAKE_KEY=anything
synthbench submit-adapter \
    --adapter synthbench.adapter \
    --vendor synthbench-demo \
    --vendor-version 0.1.0 \
    --api-env-var FAKE_KEY \
    --output-dir ./demo-submission/
```

You should see `submission.md` and `run.json` in `./demo-submission/`.
The `status` field in `run.json` will be `"scaffold"` until the
follow-up evaluation pipeline (refs #256) merges.

## Follow-up work tracked against #256

- Wire `Adapter.respond` into the `core` suite runner.
- Compute the content-addressed run hash over (adapter id, suite
  manifest, persona seeds, raw responses).
- Auto-generate the leaderboard PR body and open it via `gh`.
- CI validation of submission PRs.
