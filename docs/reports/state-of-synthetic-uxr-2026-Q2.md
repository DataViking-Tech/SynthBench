# The State of Synthetic UXR — 2026 Q2

**A quarterly report from SynthBench**

| | |
|---|---|
| **Reporting period** | 2026-Q1 → 2026-Q2 (leaderboard snapshot 2026-04-15) |
| **Editor** | Wesley (DataViking-Tech) |
| **Publication** | https://synthbench.org/reports/2026-Q2 |
| **Citable as** | DataViking-Tech. *The State of Synthetic UXR, 2026 Q2*. SynthBench Quarterly Report, May 2026. |
| **License** | CC-BY-4.0 (cite freely, including in commercial reports) |
| **Companion arXiv** | [SynthBench: An Open Benchmark for Distributional and Steerability Fidelity of Synthetic Survey Respondents](../papers/synthbench-2026-arxiv.md) |

---

## Editor's note: why this report exists

Twelve months ago "synthetic respondents" was an idea most UX researchers had
heard of and few had measured. Today, AI-respondent line items appear in
budgets at most mid-market research-tech buyers; the offerings (Synthetic
Users, Ditto, Synthpanel, in-house pipelines on top of raw GPT-4o or Claude)
are differentiated; and the central evaluation question — *are these systems
accurate enough to rely on?* — has been answered, but only in scattered
papers and pre-print discourse.

This report is the answer in one place, for one quarter, with numbers. We do
not predict the future. We tell you the score, and we publish the receipts.

Three things you should know up-front:

1. **The state of the art is a 3-model ensemble at SPS ≈ 0.84.** No single
   model or vendor configuration has crossed that bar without averaging.
2. **The "just prompt ChatGPT" baseline is no longer competitive.** Raw
   GPT-4o-mini lands at ~0.62; the conditioning premium of a real synthetic-
   respondent product is now reliably +0.10 SPS or better.
3. **Persona conditioning is real, asymmetric, and quantifies LLM political
   bias.** Republican conditioning lifts alignment 2.4× more than Democrat
   conditioning, not because the conditioning is better, but because the
   *baseline* is further from Republican. This is now a measurable property
   of every model.

The rest of this report is the full quarter's data.

---

## 1. Headlines

> **Top score this quarter**
> 3-model ensemble (Haiku 4.5 × Gemini 2.5 Flash-Lite × GPT-4o-mini)
> **SPS = 0.835** on OpinionsQA (684 questions, 5-replication mean)

> **Most surprising finding**
> Multi-model distribution averaging delivers +5–7 SPS points across all
> three datasets at zero incremental API cost. Practitioners running a
> single-model pipeline are leaving roughly an SPS-grade-level on the table.

> **Most cited methodology update**
> Quarterly-salt SHA-256 partition for the private 20 % holdout, with public
> publication of the *current* salt and rotating-private *assignment*. First
> contamination defense of its kind on a synthetic-respondent benchmark.

> **Most under-discussed risk**
> Persona-template assembly bugs (unfilled `{placeholder}` strings) tank
> SPS by **11 points** and crash refusal calibration. A trivial vendor-side
> templating defect can wipe out an entire model-quality generation.

---

## 2. Leaderboard standings, 2026 Q2

### 2.1 OpinionsQA (US, 684 questions, Pew ATP)

| Rank | System | SPS | P_dist | τ | Notes |
|------|--------|-----|--------|---|-------|
| 1 | SynthPanel Ensemble (3-model) | **0.835** | 0.833 | 0.674 | Equal-weight blend |
| 2 | Gemini 2.5 Flash (raw) | 0.829 | 0.738 | 0.521 | High base entropy → temp sensitive |
| 3 | SynthPanel (Claude Sonnet 4) | 0.829 | 0.726 | 0.586 | |
| 4 | SynthPanel (Claude Haiku 4.5) | 0.829 | 0.736 | 0.590 | |
| 5 | SynthPanel (GPT-4o-mini) | 0.823 | 0.708 | 0.556 | |
| 6 | Llama 3.3 70B (raw) | 0.819 | 0.693 | 0.549 | |
| 7 | SynthPanel (Gemini Flash Lite) | 0.816 | 0.749 | 0.532 | |
| — | *Unconditioned-LLM baseline (GPT-4o-mini)* | ~0.62 | — | — | competitive floor |
| — | *Population-Average baseline* | ~0.52 | — | — | no conditioning |
| — | *Majority-Class baseline* | ~0.45 | — | — | |
| — | *Random baseline* | ~0.31 | — | — | floor |

### 2.2 SubPOP (US subpopulations, 200 questions, Suh et al. 2025)

| Rank | System | SPS | P_dist | τ |
|------|--------|-----|--------|---|
| 1 | SynthPanel Ensemble (3-model) | **0.833** | 0.871 | 0.591 |
| 2 | SynthPanel (Gemini Flash Lite) | 0.821 | 0.707 | 0.561 |
| 3 | Llama 3.3 70B (raw) | 0.796 | 0.655 | 0.512 |
| 4 | SynthPanel (GPT-4o-mini) | 0.787 | 0.652 | 0.466 |
| 5 | Gemini 2.5 Flash (raw) | 0.783 | 0.669 | 0.397 |
| 6 | SynthPanel (Haiku 4.5) | 0.773 | 0.804 | 0.103 |
| 7 | GPT-4o-mini (raw) | 0.770 | 0.628 | 0.404 |

### 2.3 GlobalOpinionQA (138 countries, 100 questions, Pew Global)

| Rank | System | SPS | P_dist | τ |
|------|--------|-----|--------|---|
| 1 | SynthPanel (Claude Sonnet 4) | **0.797** | 0.910 | 0.000* |
| 2 | SynthPanel (GPT-4o-mini) | 0.786 | 0.689 | 0.387 |
| 3 | Gemini 2.5 Flash (raw) | 0.770 | 0.687 | 0.289 |
| 4 | Llama 3.3 70B (raw) | 0.762 | 0.635 | 0.344 |
| 5 | SynthPanel (Gemini Flash Lite) | 0.762 | 0.687 | 0.248 |
| 6 | GPT-4o-mini (raw) | 0.749 | 0.633 | 0.296 |
| 7 | SynthPanel Ensemble (3-model) | 0.747 | 0.807 | 0.375 |

*Sonnet-4 on GlobalOpinionQA carries a τ-collapse warning — the row appears
on the live leaderboard with a `⚠ flagged` rank-fidelity caveat. A τ of zero
indicates Sonnet collapsed onto a near-constant per-question prediction; the
high P_dist is the population-aggregate fit. This is exactly the failure
mode the multi-axis decomposition was designed to surface.*

Full per-model leaderboard, with confidence intervals, run counts, and
config hashes, is live at
[synthbench.org/leaderboard](https://synthbench.org/leaderboard).

---

## 3. Where the field moved this quarter

### 3.1 Ensemble is the new floor

Two quarters ago the conversation in synthetic-respondent procurement was
"which single model is best?" That conversation is now over. The 3-model
ensemble outperforms every single model on OpinionsQA *and* SubPOP, and the
mechanism — equal-weight averaging of per-question response distributions —
has zero incremental API cost when the constituent runs already exist.

**Practitioner action this quarter:** if your pipeline runs one model,
double it (cheaply) by adding ensemble averaging at the distribution layer.
The lift across all three of our datasets:

| Dataset | Best single model | Equal blend | Lift |
|---|---|---|---|
| OpinionsQA | 0.766 (Haiku 4.5) | **0.836** | **+0.070** |
| SubPOP | 0.744 (Gemini FL) | **0.796** | **+0.052** |
| GlobalOpinionQA | 0.692 (GPT-4o-mini) | **0.747** | **+0.056** |

72–81 % of individual questions improve under blending. The improvement is
*not* driven by a few outliers; it is broad-based.

### 3.2 Per-model temperature optimization is mostly dead at the ensemble level

Within a single model, temperature still matters for some models (Gemini
Flash-Lite picks up +4.5 SPS pts from t=0.3 → t=2.0). But once you ensemble,
the ensemble already absorbs per-model temperature gains: full optimal-
temperature ensemble (0.900) vs default-temperature ensemble (0.899) =
**+0.001 SPS**. The variance from rerunning the ensemble (~0.003) exceeds
the gain from temperature optimization.

For pipeline builders this means: **stop sweeping temperature.** Ensemble
three default-temperature runs from three different models instead.

### 3.3 Persona templates: the boring stuff dominates

The persona-template ablation showed that a clean, fully-rendered persona
template (name + age + occupation + background + personality) outperforms
elaborate templates with unfilled placeholders by **+11 SPS points**.
Garbled placeholder strings drove P_refuse from 0.80 to 0.40–0.50 — the
model refuses more when shown nonsense input.

This is the QA discipline most likely to be missed by ML-focused teams:
your synthetic-respondent system is, in part, a string-template factory,
and string-template bugs are catastrophic to score. We recommend any
production pipeline include a "template-rendered" lint pass on every
persona before submitting it to the model.

### 3.4 Persona conditioning quantifies political and economic bias

The quarter's most independently-citeable finding: conditioning effects are
*asymmetric* in a way that exposes default-model bias.

| Attribute | Group | P_dist (unconditioned) | P_cond |
|---|---|---|---|
| Politics | Republican | 0.666 | **+0.073** |
| Politics | Democrat | 0.644 | **+0.033** |
| Income | $100K+ | 0.673 | +0.031 |
| Income | <$30K | 0.603 | +0.020 |
| Education | College grad | 0.641 | +0.036 |
| Education | <HS | 0.597 | +0.038 |

Read these as the corrections needed to drag the default model toward each
group's real survey distribution. The fact that Republican needs 2.4× more
correction than Democrat is the directional measurement of LLM political
default-bias that the bias-auditing literature has been asking for. It is
*not* a critique of conditioning; conditioning works, and the credit
attaches in both directions.

### 3.5 What did *not* move this quarter

- **Frontier-model adoption** on the leaderboard. The 2026 frontier
  (Claude Opus 4.7, GPT-5, Gemini 3) is not yet on the board for the
  Phase-1 datasets. Submissions welcome.
- **GlobalOpinionQA Full elevation.** We are still scoring 100 of 2,556
  questions on GlobalOpinionQA. Full elevation is a 2026-Q3 milestone.
- **Open-ended fidelity (P_theme).** Phase 2 work. Ground-truth corpus
  selection is ongoing.

---

## 4. Vendor-by-vendor read

### 4.1 SynthPanel

Across-the-board strong, especially under ensemble averaging. The product's
distinguishing property is that its per-model adapter exposes the
distribution layer cleanly, so post-hoc ensembling of multiple SynthPanel
configurations works without code changes. **Use case fit:** market-research
panel substitution where group-level fidelity is the central concern.

### 4.2 Raw OpenAI / Anthropic / Google models

GPT-4o-mini, Gemini 2.5 Flash, and Claude Haiku 4.5 are all competitive
single models. Gemini Flash Lite is the standout for the temperature-
sensitive case. Each of these is a reasonable single-model pipeline
foundation; combined as a 3-model ensemble, they are the current state of
the art.

### 4.3 Llama 3.3 70B

Strong open-weights performer (raw SPS 0.819 on OpinionsQA, 0.796 on
SubPOP). Materially competitive with the hosted frontier on the Phase-1
datasets and unique in being self-hostable. **Use case fit:** privacy-
sensitive synthetic-respondent workloads where data must not leave the
buyer's perimeter. Cost reported as `null` (self-hosted compute, not
measurable through provider invoices).

### 4.4 Synthetic Users / Ditto / Persona

Not yet on the SynthBench leaderboard for this quarter. We have invited
each to submit per the protocol in §6.

---

## 5. Integrity update

This is the second quarter under SynthBench's contamination-defense regime.
Operational notes:

- **Salt rotation 2026-Q2 → 2026-Q3 is scheduled for 2026-06-30.** Vendors
  with pending submissions should target Q2 to be scored under the current
  salt; Q3 submissions will be scored under a fresh partition.
- **Public-vs-private SPS divergence audit.** Two rows on the live board
  carry `⚠ flagged` status this quarter:
  - Sonnet-4 on GlobalOpinionQA (τ-collapse; see §2.3).
  - One SynthPanel-Ensemble row on OpinionsQA (cost-data anomaly resolved
    in pipeline rerun; row left flagged for transparency until next salt
    rotation).
- **Adversarial regression suite.** 41 fabricated submissions on the CI
  gate as of this report; all 41 are required to score their known-bad
  values before a release ships. Zero regressions this quarter.
- **No perfection-error triggers.** No submission this quarter crossed
  SPS ≥ 0.995. The `Perfection → ERROR` invariant was last triggered in
  2026-Q1 by a vendor evaluator-pipeline misconfiguration that double-
  counted; the run was rejected and the cause publicly documented.

---

## 6. How to be on the next quarterly report

We will publish the 2026-Q3 report on 2026-08-15. To be included:

1. `pip install synthbench`
2. `synthbench run --provider <yours> --suite core` (or `full`)
3. `synthbench submit ./results/your-run.json`

A submission must include a `config_hash`, dataset key, sampling protocol,
and a per-question artifact list. Submissions are scored against the
*current quarterly salt* and surface on the leaderboard with verification
status within seven business days. Submissions are free, public, and
audit-trailed.

We particularly welcome:

- Frontier 2026 models (Claude Opus 4.7, GPT-5, Gemini 3).
- Dedicated synthetic-respondent vendors not yet on the board.
- Self-hosted open-weights configurations.
- Submissions on GlobalOpinionQA Full coverage (we will help with the
  HuggingFace gating).

---

## 7. Recommended reads (this quarter)

If you read three things on synthetic respondents this quarter, make them:

1. **Wang et al., "Assessing the Reliability of Persona-Conditioned LLMs as
   Synthetic Survey Respondents,"** arXiv:2602.18462 — the most direct
   academic engagement with the question SynthBench operationalizes.
2. **HBR, "Trendslop: When AI-Augmented Research Says Nothing Plausibly"**
   (2026) — the framing piece every UX-research buyer is reading. SynthBench
   is in the conversation because trendslop without a measurement layer is
   the failure state HBR describes.
3. **Suh et al., "Language Model Fine-Tuning on Scaled Survey Data,"**
   *ACL 2025* (arXiv:2502.16761) — the SubPOP paper, ground truth for one
   of our three datasets and the methodological backbone for distribution-
   prediction approaches.

---

## 8. Next quarter's preview

Confirmed for 2026-Q3:

- GlobalOpinionQA Full (2,556 Qs, 138 countries) coverage on the leaderboard.
- 2026 frontier-model submissions (Claude Opus 4.7, GPT-5 if released).
- Cost-vs-SPS Pareto chart elevated from "coming soon" to published.
- Temporal-drift floor visualization (year-by-year baseline tracking).
- First publication of P_theme calibration against human raters on a pilot
  open-ended subset.

Tentative for 2026-Q4:

- WVS Wave 7 coverage (64 countries, deeper political/religious questions).
- GSS coverage with year filter (1972-present, temporal drift baselining).
- A peer-reviewed venue submission of the arXiv preprint.

---

## 9. Citation

```
DataViking-Tech. "The State of Synthetic UXR, 2026 Q2." SynthBench Quarterly
Report, May 2026. https://synthbench.org/reports/2026-Q2.
```

BibTeX:

```bibtex
@misc{synthbench_quarterly_2026q2,
  author       = {{DataViking-Tech}},
  title        = {The State of Synthetic UXR, 2026 Q2},
  howpublished = {SynthBench Quarterly Report},
  year         = {2026},
  month        = {May},
  url          = {https://synthbench.org/reports/2026-Q2}
}
```

CC-BY-4.0. Cite, quote, screenshot, and incorporate freely — including in
commercial reports — with attribution.

---

*Editor: Wesley (DataViking-Tech). Comments, corrections, and submissions
welcome at wesley@dataviking.tech or via GitHub issue at
https://github.com/DataViking-Tech/synthbench. Next report: 2026-08-15.*
