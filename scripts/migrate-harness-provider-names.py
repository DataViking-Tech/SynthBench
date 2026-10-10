#!/usr/bin/env python3
"""Rename harness runs to vendor/model + harness= tag (one-off, 2026-10-10).

The first althing subscription-CLI runs were recorded with the harness as
part of the model name (``althing/claude-code:haiku``). Harness runs are now
named after the vendor and the model the CLI served, with the harness as a
knob (``althing/anthropic/claude-haiku-5-5 harness=claude-code``), so they
group with the vendor and get a harness tag on the site.

For each result file whose provider uses the old form this script:

- rewrites ``config.provider`` and adds ``config.harness``;
- recomputes ``model_revision_hash`` (sha256 of the provider name) in both
  ``config`` and ``reproducibility``;
- updates the provider line in the sibling ``.md`` score card;
- renames both files to the slug ``report.save`` would produce now.

Only metadata changes; scores and per-question rows are untouched.

Usage: python scripts/migrate-harness-provider-names.py [--dry-run]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from synthbench.report import provider_slug

RESULTS = Path(__file__).resolve().parent.parent / "leaderboard-results"

# Old model segment -> (harness, vendor, served model). `claude-code:haiku`
# resolved to claude-haiku-5-5 for every run recorded under the old form.
OLD_MODELS = {
    "claude-code:haiku": ("claude-code", "anthropic", "claude-haiku-5-5"),
    "codex:gpt-6-luna": ("codex", "openai", "gpt-6-luna"),
}


def new_provider(provider: str) -> tuple[str, str] | None:
    head, _, knobs = provider.partition(" ")
    framework, _, model = head.partition("/")
    if framework != "althing" or model not in OLD_MODELS:
        return None
    harness, vendor, served = OLD_MODELS[model]
    parts = [f"althing/{vendor}/{served}", f"harness={harness}"]
    if knobs:
        parts.append(knobs)
    return " ".join(parts), harness


def main(dry_run: bool) -> int:
    changed = 0
    for path in sorted(RESULTS.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        cfg = data.get("config") or {}
        old = cfg.get("provider", "")
        res = new_provider(old)
        if res is None:
            continue
        provider, harness = res
        digest = "sha256:" + hashlib.sha256(provider.encode("utf-8")).hexdigest()
        cfg["provider"] = provider
        cfg["harness"] = harness
        if "model_revision_hash" in cfg:
            cfg["model_revision_hash"] = digest
        repro = data.get("reproducibility")
        if isinstance(repro, dict) and "model_revision_hash" in repro:
            repro["model_revision_hash"] = digest

        stamp = path.stem.rsplit("_", 2)[-2:]
        new_stem = f"{cfg.get('dataset', 'unknown')}_{provider_slug(provider)}_{'_'.join(stamp)}"
        md = path.with_suffix(".md")
        print(f"{path.name}\n  -> {new_stem}.json\n  provider: {old!r} -> {provider!r}")
        changed += 1
        if dry_run:
            continue
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        path.rename(path.with_name(f"{new_stem}.json"))
        if md.exists():
            md.write_text(
                md.read_text(encoding="utf-8").replace(old, provider), encoding="utf-8"
            )
            md.rename(md.with_name(f"{new_stem}.md"))
    print(f"{changed} file(s) {'would be ' if dry_run else ''}migrated")
    return 0


if __name__ == "__main__":
    sys.exit(main("--dry-run" in sys.argv[1:]))
