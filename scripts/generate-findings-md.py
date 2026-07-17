#!/usr/bin/env python3
"""Regenerate the generated sections of FINDINGS.md from leaderboard-results/.

Every quantitative table between ``<!-- BEGIN GENERATED: name -->`` /
``<!-- END GENERATED: name -->`` markers is rendered from the same
computation that feeds the published findings block
(``synthbench.findings.build_findings``), so FINDINGS.md can never drift
from the artifacts without CI noticing (tests/test_findings_drift.py).

Usage:
    python scripts/generate-findings-md.py            # rewrite FINDINGS.md
    python scripts/generate-findings-md.py --check    # exit 1 on drift
"""

from __future__ import annotations

import argparse
import difflib
import logging
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

MARKER_RE = re.compile(
    r"<!-- BEGIN GENERATED: (?P<name>[\w-]+) -->\n"
    r".*?"
    r"<!-- END GENERATED: (?P=name) -->",
    re.DOTALL,
)


def _pts(delta: float) -> str:
    return f"{delta * 100:+.1f}"


def _fmt(value: float, places: int = 3) -> str:
    return f"{value:.{places}f}"


def _std_str(row: dict) -> str:
    std = row.get("std")
    return f" ± {std:.3f}" if std is not None else ""


def render_headline(f: dict) -> str:
    lines = [
        f"**Metric convention**: all SPS values below use the `{f['sps_convention']}` "
        "composite (equal-weighted mean of all available components), recomputed "
        "from per-question rows at publish time (#305). Random baselines score "
        + "/".join(
            _fmt(e["random_baseline_sps"])
            for e in f["ensemble_comparison"]
            if "random_baseline_sps" in e
        )
        + " on this scale ("
        + ", ".join(
            e["dataset"] for e in f["ensemble_comparison"] if "random_baseline_sps" in e
        )
        + ") — read every headline against that floor, not against 0.",
        "",
        "| Dataset | 3-model ensemble SPS | Best single model | Random baseline |",
        "|---------|---------------------|-------------------|-----------------|",
    ]
    for e in f["ensemble_comparison"]:
        rb = (
            f"{_fmt(e['random_baseline_sps'])} (n={e['random_baseline_n']})"
            if "random_baseline_sps" in e
            else "—"
        )
        lines.append(
            f"| {e['dataset']} (n={e['n_questions']}) | **{_fmt(e['ensemble_sps'])}** | "
            f"{_fmt(e['best_single_sps'])} ({e['best_single_model']}, "
            f"{e['best_single_framework']}) | {rb} |"
        )
    return "\n".join(lines)


def render_temperature(f: dict) -> str:
    per_model: dict[str, list[dict]] = {}
    for p in f["temperature_sweep"]:
        per_model.setdefault(p["model"], []).append(p)
    lines = [
        "| Model | Temp range | SPS range (mean) | Δ (pts) | Replications/cell |",
        "|-------|-----------|------------------|---------|-------------------|",
    ]
    for model in sorted(per_model):
        pts = sorted(per_model[model], key=lambda p: p["temperature"])
        lo, hi = min(p["sps"] for p in pts), max(p["sps"] for p in pts)
        reps = sorted({p["n_runs"] for p in pts})
        reps_s = "–".join(str(r) for r in (reps if len(reps) > 1 else reps))
        lines.append(
            f"| {model} | {pts[0]['temperature']}–{pts[-1]['temperature']} | "
            f"{_fmt(lo)}–{_fmt(hi)} | {_pts(hi - lo)} | {reps_s} |"
        )
    lines += [
        "",
        "Full sweep (mean ± std across replications):",
        "",
        "| Model | Temp | SPS | n |",
        "|-------|------|-----|---|",
    ]
    for p in f["temperature_sweep"]:
        lines.append(
            f"| {p['model']} | {p['temperature']} | "
            f"{_fmt(p['sps'])}{_std_str(p)} | {p['n_runs']} |"
        )
    return "\n".join(lines)


def render_template(f: dict) -> str:
    lines = [
        "| Template | Mean SPS | Std | Runs |",
        "|----------|----------|-----|------|",
    ]
    for t in f["template_comparison"]:
        best = "**" if t is f["template_comparison"][0] else ""
        std = f"{t['std']:.3f}" if "std" in t else "—"
        lines.append(
            f"| {best}{t['template'].upper()}{best} | {best}{_fmt(t['sps'])}{best} "
            f"| {std} | {t['n_runs']} |"
        )
    if len(f["template_comparison"]) > 1:
        best = f["template_comparison"][0]
        runner = f["template_comparison"][1]
        lines += [
            "",
            f"The {best['template'].upper()} template beats the best alternative "
            f"by **{_pts(best['sps'] - runner['sps'])} SPS points**.",
        ]
    return "\n".join(lines)


def _conditioning_table(rows: list[dict]) -> list[str]:
    lines = [
        "| Group | P_dist | P_cond | Replications |",
        "|-------|--------|--------|--------------|",
    ]
    for r in rows:
        std = f" ± {r['p_cond_std']:.3f}" if "p_cond_std" in r else ""
        lines.append(
            f"| {r['group']} | {_fmt(r['p_dist'])} | "
            f"**{_fmt(r['p_cond'])}{std}** | {r['n_replications']} |"
        )
    return lines


def _ratio(rows: list[dict], attribute: str) -> float | None:
    vals = [r["p_cond"] for r in rows if r["attribute"] == attribute]
    if len(vals) < 2 or min(vals) <= 0:
        return None
    return max(vals) / min(vals)


def render_conditioning(f: dict) -> str:
    rows = f["conditioning_results"]
    out: list[str] = []
    for attribute in ("POLPARTY", "INCOME", "EDUCATION"):
        sub = [r for r in rows if r["attribute"] == attribute]
        if not sub:
            continue
        out.append(f"#### {attribute}")
        out.append("")
        out.extend(_conditioning_table(sub))
        out.append("")
    pol = _ratio(rows, "POLPARTY")
    inc = _ratio(rows, "INCOME")
    if pol is not None:
        out.append(
            f"Republican conditioning is **{pol:.1f}× stronger** than Democrat "
            f"(mean P_cond across replications)."
        )
    if inc is not None:
        out.append(
            f"High-income conditioning is **{inc:.1f}× stronger** than low-income."
        )
    ext = f.get("conditioning_extended") or []
    if ext:
        out += [
            "",
            "#### Other measured attributes",
            "",
        ]
        lines = [
            "| Attribute | Group | P_dist | P_cond | Replications |",
            "|-----------|-------|--------|--------|--------------|",
        ]
        for r in ext:
            std = f" ± {r['p_cond_std']:.3f}" if "p_cond_std" in r else ""
            lines.append(
                f"| {r['attribute']} | {r['group']} | {_fmt(r['p_dist'])} | "
                f"{_fmt(r['p_cond'])}{std} | {r['n_replications']} |"
            )
        out.extend(lines)
    return "\n".join(out)


def render_ensemble(f: dict) -> str:
    lines = [
        "| Dataset | Best single model | Equal blend | Improvement | Random baseline |",
        "|---------|-------------------|-------------|-------------|-----------------|",
    ]
    for e in f["ensemble_comparison"]:
        rb = (
            f"{_fmt(e['random_baseline_sps'])} (n={e['random_baseline_n']})"
            if "random_baseline_sps" in e
            else "—"
        )
        lines.append(
            f"| {e['dataset']} ({e['n_questions']}q) | "
            f"{_fmt(e['best_single_sps'])} ({e['best_single_model']}, "
            f"{e['best_single_framework']}) | **{_fmt(e['ensemble_sps'])}** | "
            f"**{_pts(e['improvement'])} pts** | {rb} |"
        )
    lines += [
        "",
        f"Comparison set: {f['comparison_sets']['ensemble_comparison']}",
    ]
    for caveat in f.get("caveats") or []:
        lines += ["", f"> **Caveat**: {caveat}"]
    return "\n".join(lines)


def render_extended_temperature(f: dict) -> str:
    pts = [
        p
        for p in f["temperature_sweep"]
        if p["model"] == "Gemini Flash Lite" and p["temperature"] >= 1.0
    ]
    pts.sort(key=lambda p: p["temperature"])
    lines = ["| Temp | Mean SPS | n |", "|------|----------|---|"]
    for p in pts:
        bold = "**" if p is pts[-1] else ""
        lines.append(
            f"| {bold}{p['temperature']}{bold} | "
            f"{bold}{_fmt(p['sps'])}{_std_str(p)}{bold} | {p['n_runs']} |"
        )
    return "\n".join(lines)


def render_levers(f: dict) -> str:
    lines = [
        "| Lever | Effect size (SPS pts) | Cost | Status |",
        "|-------|----------------------|------|--------|",
    ]
    for lv in f["lever_hierarchy"]:
        if lv["effect_min"] == lv["effect_max"] == 0.0:
            effect = lv.get("note", "no further gain")
        else:
            effect = f"+{lv['effect_min']}–{lv['effect_max']}"
        lines.append(f"| **{lv['name']}** | {effect} | {lv['cost']} | {lv['status']} |")
    return "\n".join(lines)


def render_nonresponse(f: dict) -> str:
    rows = f.get("nonresponse_fidelity") or []
    if not rows:
        return "_No runs with committed human distributions available._"
    lines = [
        "| Provider | Framework | Template | Dataset | Mean model nonresponse | "
        "Mean human nonresponse | Mean abs gap | n |",
        "|----------|-----------|----------|---------|------------------------|"
        "------------------------|--------------|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['provider']} | {r['framework']} | "
            f"{r.get('template') or 'default'} | {r['dataset']} | "
            f"{_fmt(r['mean_model_nonresponse_mass'])} | "
            f"{_fmt(r['mean_human_nonresponse_mass'])} | "
            f"**{_fmt(r['mean_abs_nonresponse_gap'])}** | {r['n_questions']} |"
        )
    lines += ["", f"Comparison set: {f['comparison_sets']['nonresponse_fidelity']}"]

    s = f.get("sensitive_topic_sidestepping")
    if s:
        lines += [
            "",
            f"**{s['headline']}** ({s['provider']}, {s['dataset']}, "
            f"n={s['n_questions']}): mean model nonresponse mass "
            f"{_fmt(s['mean_model_nonresponse_mass'])} vs human "
            f"{_fmt(s['mean_human_nonresponse_mass'])}. Worst items:",
            "",
            "| Item | Model nonresponse | Human nonresponse |",
            "|------|-------------------|-------------------|",
        ]
        for i in s["items"]:
            lines.append(
                f"| {i['key']} | {i['model_mass'] * 100:.0f}% | "
                f"{i['human_mass'] * 100:.1f}% |"
            )
        lines += ["", s["note"]]
    return "\n".join(lines)


def render_asserted(f: dict) -> str:
    lines = [
        "The following claims are **not derivable from the committed artifacts** "
        "and are carried as asserted constants (also published in the findings "
        "block's `asserted_constants` list, which the CI drift guard checks):",
        "",
        "| Claim | Source |",
        "|-------|--------|",
    ]
    for c in f["asserted_constants"]:
        lines.append(f"| {c['value']} | {c['source']} |")
    return "\n".join(lines)


RENDERERS = {
    "headline": render_headline,
    "temperature": render_temperature,
    "template": render_template,
    "conditioning": render_conditioning,
    "ensemble": render_ensemble,
    "extended-temperature": render_extended_temperature,
    "levers": render_levers,
    "nonresponse-fidelity": render_nonresponse,
    "asserted-constants": render_asserted,
}


def regenerate(text: str, findings: dict) -> str:
    seen: set[str] = set()

    def _sub(m: re.Match) -> str:
        name = m.group("name")
        seen.add(name)
        renderer = RENDERERS.get(name)
        if renderer is None:
            raise SystemExit(f"FINDINGS.md has unknown generated section: {name!r}")
        return (
            f"<!-- BEGIN GENERATED: {name} -->\n"
            f"{renderer(findings)}\n"
            f"<!-- END GENERATED: {name} -->"
        )

    out = MARKER_RE.sub(_sub, text)
    missing = set(RENDERERS) - seen
    if missing:
        raise SystemExit(
            f"FINDINGS.md is missing generated sections: {sorted(missing)}"
        )
    return out


def build(findings_md: Path, results_dir: Path) -> tuple[str, str]:
    from synthbench.findings import build_findings, load_valid_results

    logging.disable(logging.WARNING)  # silence expected recompute-divergence noise
    results, excluded = load_valid_results(results_dir)
    findings = build_findings(results, excluded)
    original = findings_md.read_text()
    return original, regenerate(original, findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 on drift")
    parser.add_argument("--findings-md", type=Path, default=REPO_ROOT / "FINDINGS.md")
    parser.add_argument(
        "--results-dir", type=Path, default=REPO_ROOT / "leaderboard-results"
    )
    args = parser.parse_args()

    original, regenerated = build(args.findings_md, args.results_dir)
    if args.check:
        if original != regenerated:
            sys.stderr.write(
                "FINDINGS.md generated sections are stale — run "
                "scripts/generate-findings-md.py\n"
            )
            sys.stderr.writelines(
                difflib.unified_diff(
                    original.splitlines(keepends=True),
                    regenerated.splitlines(keepends=True),
                    "committed FINDINGS.md",
                    "regenerated",
                )
            )
            return 1
        print("FINDINGS.md generated sections are up to date.")
        return 0

    if original != regenerated:
        args.findings_md.write_text(regenerated)
        print(f"Rewrote generated sections in {args.findings_md}")
    else:
        print("No changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
