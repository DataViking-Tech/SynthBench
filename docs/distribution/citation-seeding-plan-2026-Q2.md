# Citation Seeding Plan — 2026 Q2

**Goal:** ≥3 third-party citations of SynthBench in 90 days (window:
2026-05-14 → 2026-08-12). Mirrors GH#258 ("Authoritativeness flywheel").
**Owner:** Wesley
**Companion artifacts:**
- [arXiv preprint, v1](../papers/synthbench-2026-arxiv.md) (Track 3a)
- [State of Synthetic UXR Q2-2026](../reports/state-of-synthetic-uxr-2026-Q2.md) (Track 3b)
- This plan (Track 3c)

---

## What "citation" counts toward the goal

A citation is **a publication, post, podcast, newsletter, or product page —
not authored or commissioned by us — that names "SynthBench" and links to
synthbench.org or the arXiv preprint.** Quality tiers:

| Tier | Example | Counts as | Why |
|---|---|---|---|
| **S** | Peer-reviewed paper citing the arXiv preprint | 1.0 | The credibility anchor |
| **A** | Top-tier industry newsletter (Ben Thompson, Ethan Mollick, Latent Space, Last Week in AI) | 1.0 | Distribution to the buyer audience |
| **A** | A major analyst note (Gartner, Forrester, CB Insights) | 1.0 | Procurement validation |
| **B** | A vendor (Synthetic Users, Ditto, etc.) referencing SynthBench in their own marketing | 1.0 | The flywheel signal — vendors validate us by using us |
| **B** | A practitioner blog post with code reproducing a SynthBench result | 1.0 | Reproducibility signal |
| **C** | Subreddit thread (r/UXResearch, r/MarketResearch, r/LocalLLaMA) with substantive discussion | 0.5 | Audience engagement signal |
| **C** | Substack / LinkedIn newsletter post by a recognized practitioner | 0.5 | |
| **D** | Tweet / retweet that links the site | 0.1 | Background noise |

Target: **3.0 weighted citation-points** across S–B in 90 days, with at
least one S or A.

---

## Distribution targets, ranked by reach ÷ effort

The ranking below is conservative. Effort is one-engineer-hours assuming the
arXiv preprint and the Q2 report are already drafted (they are).

### Tier S — ship this week (table stakes)

| # | Target | Channel | Effort | Reach | Status |
|---|---|---|---|---|---|
| 1 | **arXiv submission** | arXiv cs.CL primary, cs.HC + stat.AP cross-list | 2h (LaTeX conversion) | Mid (per submission), Enormous (long tail) | Manuscript ready in `docs/papers/synthbench-2026-arxiv.md`; needs LaTeX conversion + endorsement (Wesley has one) |
| 2 | **Hugging Face dataset card** for `leaderboard-results/` | HuggingFace Datasets | 0.5d | High (researcher discovery) | Cross-referenced in arXiv §9 |
| 3 | **Papers With Code listing** | papers-with-code.com | 2h | Mid-high | Pairs with arXiv submission ID |
| 4 | **Hacker News submission** | HN, off-hours US east | 30 min | Mid (decaying, but spiky) | Submit Q2 report, not arXiv (report is more readable to HN crowd) |

### Tier A — ship within 2 weeks (high-yield outreach)

| # | Target | Outreach | Effort | Reach |
|---|---|---|---|---|
| 5 | **Latent Space (swyx + Alessio)** | Direct email pitch: "we built the MLPerf of synthetic UXR; would you want a demo / podcast?" | 1h + 30min recording | Very high in AI-eng |
| 6 | **Ethan Mollick (One Useful Thing)** | Email or DM with the conditioning-asymmetry finding as the hook (politically-revealing benchmark) | 30 min | Very high, decisive credibility |
| 7 | **Last Week in AI** | Email Andrey & Sharon with the Q2 report; offer arXiv preprint as exclusive on submission week | 30 min | High |
| 8 | **Ben Thompson (Stratechery)** | Long-shot but worth one pitch on the "trendslop" angle (HBR framing → SynthBench measures the antidote) | 30 min | Enormous if it lands |
| 9 | **The Sequence (Jesús Rodríguez)** | Email pitch focused on the methodology paper, audience is technical AI practitioners | 30 min | High |
| 10 | **Import AI (Jack Clark)** | Email pitch focused on the contamination defenses + integrity stack — Jack writes about benchmark integrity | 30 min | High |
| 11 | **The Algorithmic Bridge (Alberto Romero)** | Pitch the political-conditioning asymmetry finding as a stand-alone post | 30 min | Mid-high |

### Tier B — academic and practitioner targets (2–4 weeks)

| # | Target | Channel | Effort | Reach |
|---|---|---|---|---|
| 12 | **Stanford HAI / CRFM Slack + newsletter** | Submit via the CRFM benchmark intake form | 1h | High in research |
| 13 | **Berkeley AgentBench / Stanford HELM teams** | Direct email referencing our citation of their contamination work (we built on it) | 30 min | High signal-to-noise |
| 14 | **EleutherAI Discord, #benchmarks** | Post link + ask for feedback | 15 min | Mid |
| 15 | **MLCommons / MLPerf community** | The "MLPerf of synthetic UXR" framing is the natural hook | 1h to find the right contact | Mid-high |
| 16 | **NeurIPS Datasets & Benchmarks track** | Workshop submission cycle (deadline 2026-Q3) | 1 week | Enormous long-term |

### Tier C — subreddit and community seeding (1–3 weeks, light touch)

| # | Subreddit / forum | Hook | Effort | Notes |
|---|---|---|---|---|
| 17 | **r/UXResearch** (180K) | Share the Q2 report. *Soft.* Don't drop the link first — comment substantively on existing threads about AI panel risks, link in profile. | 2h over 2 weeks | UX researchers are skeptical of synthetic respondents; SynthBench is on their side. |
| 18 | **r/MarketResearch** (45K) | Same as r/UXResearch, with emphasis on Pew ground truth | 2h | |
| 19 | **r/LocalLLaMA** (~800K) | Lead with Llama 3.3 70B holding top-5 on a serious benchmark. *That's the hook.* | 1h | Has a deep history of citing benchmarks |
| 20 | **r/MachineLearning** | "We built a benchmark that fights contamination with quarterly salt rotation. AMA." | 2h | High moderation bar — must be substantive |
| 21 | **r/UserExperience** (~1M) | Cross-post of r/UXResearch content if it lands | 30 min | |
| 22 | **HN /show** | Submit the Q2 report (not arXiv — wrong audience) | 30 min | Re-submit at off-hours if first attempt dies |
| 23 | **Lobste.rs** | Submit if HN does well | 15 min | |

### Tier D — newsletters / Substacks (rolling)

| # | Target | Hook | Effort |
|---|---|---|---|
| 24 | **Greenbook Daily (mrweb.com / Greenbook)** — *market-research industry trade press* | The Q2 report, as a citable secondary source | 30 min |
| 25 | **GreenBook IIEX Insights** | Quarterly trends — natural fit for the Q2 cadence | 30 min |
| 26 | **Quirk's Marketing Research Media** | Same as Greenbook | 30 min |
| 27 | **Research-Live (UK market research)** | Same | 30 min |
| 28 | **Substack: NN/g (Nielsen Norman Group)** | Long-shot but they cover UXR rigor topics | 30 min |
| 29 | **Substack: AI Snake Oil (Arvind Narayanan + Sayash Kapoor)** | Pitch: "we built a benchmark resistant to the failure modes you write about" | 30 min |
| 30 | **Substack: Marginalia / Bytes & Borscht / Interconnected** | Long-tail, rolling | 30 min each |

---

## What to send: pre-written outreach

### A. Cold email template (newsletter authors)

```
Subject: Benchmark for synthetic survey respondents — preprint + Q2 report

Hi [name],

I'm Wesley, building SynthBench — an open benchmark that measures how
faithfully AI systems reproduce real human survey distributions
(Pew/SubPOP/Global ground truth, 7,400+ questions). It's the
"MLPerf of synthetic UXR" for the UX/market-research and AI-eval crowd.

Two artifacts you might find useful:

1. Preprint with the methodology + adversarial-integrity stack (private
   20% holdout, quarterly salt rotation, perfection-flag invariant):
   <arXiv link once submitted>

2. Q2 report with leaderboard standings — current state of the art is
   SPS ≈ 0.84 from a 3-model ensemble (zero incremental cost finding),
   and the persona-conditioning asymmetry quantifies LLM political-default
   bias at calibration grade:
   https://synthbench.org/reports/2026-Q2

Happy to chat about [the most-relevant-finding for THIS audience],
ship a demo, or send raw data. No follow-up obligation either way.

Wesley
wesley@dataviking.tech
github.com/DataViking-Tech/synthbench
```

**Per-recipient customization** lives in the bracketed bits. Ethan Mollick
gets the persona-asymmetry hook. swyx gets the contamination defenses
hook. Ben Thompson gets the trendslop hook. Andrey Kurenkov gets the
methodology hook.

### B. Subreddit lead post template (r/UXResearch / r/MarketResearch)

```
Title: A new open benchmark for AI synthetic respondents (Pew ATP +
SubPOP ground truth) — we publish the scoring receipts

I work on a public benchmark called SynthBench that measures whether AI
systems ("synthetic users") actually reproduce real survey response
distributions. We score 7,400+ questions across OpinionsQA, SubPOP, and
GlobalOpinionQA, decompose the score into 5 axes (distribution, rank,
conditioning, subgroup, refusal), and publish every per-question artifact.

Three findings I think are useful for working UX/MR folks:

1. Raw "just prompt ChatGPT" is at SPS ~0.62. Real synthetic-respondent
   products clear ~0.82. The conditioning premium is now measurable.

2. Multi-model ensemble averaging (3 cheap models) clears 0.84. At zero
   API cost. If your AI-panel pipeline runs one model, you're leaving an
   SPS letter-grade on the table.

3. Republican conditioning shifts the model 2.4x more than Democrat
   conditioning — not because conditioning is better, but because the
   *baseline* is further from Republican. This quantifies LLM political
   defaults with calibration-grade signal.

Q2 report: https://synthbench.org/reports/2026-Q2
Methodology: https://synthbench.org/methodology
GitHub: github.com/DataViking-Tech/synthbench

Happy to answer methodology / replication questions. I built this in
the open *because* the field needs a non-vendor measurement layer.
```

### C. Vendor outreach template (to Synthetic Users, Ditto, etc.)

```
Subject: SynthBench submission — would you score?

Hi [name],

SynthBench (synthbench.org) is the open leaderboard for synthetic survey
respondents. Current top result is SPS ~0.84 (3-model ensemble); the
unconditioned-LLM baseline sits at ~0.62.

I'd love to score [Product X] on the public board. The submission
protocol is `pip install "synthbench-eval @ git+https://github.com/DataViking-Tech/SynthBench.git"
&& synthbench run --provider <yours>
--suite core`. Submission is free, public, audit-trailed, and you keep
the per-question outputs.

If the score is below where you'd want, we publish it anyway — but with
the *full sub-score decomposition*, so it's clear which axis to improve.
That tends to be more useful for product planning than a vanity number.

Want to run a private dry-run first? I'll help you wire up the adapter
and you can withhold submission until you're satisfied.

Wesley
wesley@dataviking.tech
```

**Why this works:** vendors who are confident submit and brag. Vendors
who are uncertain take the dry-run and tune their product first. Either
outcome is good for SynthBench's authoritativeness.

---

## What NOT to do

- **Do not pay for placement.** Sponsored content reads as paid and
  undermines the integrity posture.
- **Do not astroturf subreddits.** One real account, real history of
  participation, never the first link in a thread. The win condition is
  *being cited by others*, not *being posted by us*.
- **Do not run a Twitter giveaway.** Wrong audience.
- **Do not pitch generic "AI tools" newsletters.** SynthBench is not a
  tool the audience uses; it is a measurement layer they cite. Pitch
  measurement/eval venues, not tool venues.
- **Do not over-promise on the arXiv timeline.** v1 is preprint; peer
  review (NeurIPS D&B, ACL Findings, EMNLP) is a Q3+ effort.
- **Do not bury the integrity story.** Every pitch should mention the
  private-holdout / quarterly-salt design somewhere — it's the
  differentiator that AI-engineer audiences respond to (see
  ai-engineer-readiness.md §2).

---

## Tracking and measurement

We track in a single bead with weekly updates:

| Week of | Target hit | Tier | Citation | Weighted points |
|---|---|---|---|---|
| 2026-05-19 | (placeholder) | — | — | 0.0 |
| ... | | | | |

Source of truth: `bd update sb-v6a --notes "..."` each Friday until the
90-day window closes (2026-08-12). At that point, the cumulative weighted-
point total goes in the 2026-Q3 quarterly report's §5 ("Integrity update"
section is the natural home; a successful flywheel is itself an integrity
signal).

### Leading indicators (track weekly)

- Unique referrers to synthbench.org from outside our own domains.
- arXiv abstract-page views and PDF downloads (post-submission).
- Hugging Face dataset card views and downloads.
- GitHub stars (vanity, but a useful leading indicator of academic citation
  by ~6-month lag).
- "synthbench" Twitter / X mention count (via a saved search).
- "synthbench" Google Scholar hits (monthly check).

### Lagging indicators (track at 90-day window close)

- Cumulative weighted citation points (target: ≥3.0).
- Number of unique S/A-tier citations (target: ≥1).
- Number of vendor submissions to the public board (target: ≥2 vendors not
  named SynthPanel).
- Inbound research-data-access requests via the protocol in
  `METHODOLOGY.md §8` (target: ≥3 — these are credible-researcher signal).

---

## Concrete week-by-week schedule

### Week 1 (2026-05-14 → 2026-05-20)

- [ ] LaTeX conversion of arXiv manuscript (Tier S #1)
- [ ] Obtain arXiv endorsement / submit (Tier S #1)
- [ ] Publish Q2 report on synthbench.org/reports/2026-Q2
- [ ] HuggingFace dataset card for leaderboard-results (Tier S #2)
- [ ] Papers With Code listing (Tier S #3)
- [ ] HN /show submission of Q2 report (Tier S #4, end-of-week)

### Week 2 (2026-05-21 → 2026-05-27)

- [ ] Cold-pitch Tier A targets #5–11 (one per day, Monday–Friday)
- [ ] r/LocalLLaMA post led by the Llama 3.3 70B leaderboard placement
- [ ] Vendor outreach to Synthetic Users + Ditto (Tier B vendor submissions)

### Week 3 (2026-05-28 → 2026-06-03)

- [ ] Stanford CRFM intake form + Berkeley AgentBench team email
- [ ] EleutherAI Discord post
- [ ] r/UXResearch substantive participation begins (NOT first-link
      posting; comment-then-link cadence)

### Weeks 4–6 (June)

- [ ] Trade-press newsletters (Greenbook, Quirk's, Research-Live)
- [ ] Substack outreach (AI Snake Oil, NN/g)
- [ ] First weekly Friday bd-notes update on citation tracking

### Weeks 7–9 (July)

- [ ] NeurIPS D&B workshop submission preparation
- [ ] Quarterly-salt rotation 2026-Q3 (2026-06-30), publish rotation note
- [ ] Mid-window citation review; reroute effort to whichever channel
      has shown highest yield in first six weeks

### Weeks 10–13 (August → 2026-08-12 close)

- [ ] Final outreach push to any high-priority target that has not
      responded
- [ ] 2026-Q3 quarterly report drafted (deadline 2026-08-15), which
      includes the citation-flywheel scorecard in §5
- [ ] `bd close sb-v6a` with the cumulative weighted points and a
      retrospective on what worked

---

## Escalation triggers

If by **2026-06-30 (mid-window)** the weighted citation count is below
**1.0**, escalate to wesley:

```bash
gt mail send synth_bench/witness -s "Citation flywheel: mid-window
underperformance" -m "Weighted citation count <1.0 at midpoint. Likely
causes and recommended pivots: (a) ..., (b) ..."
```

Likely pivots if midpoint underperforms:

1. **Move from cold-pitch to demo-first.** Offer a live SynthBench demo
   recording session to the top three unresponsive newsletters.
2. **Publish a *second*, narrower piece** with one strong finding —
   probably the persona-conditioning asymmetry result — as a standalone
   essay on synthbench.org that is easier to cite than the full
   methodology paper.
3. **Direct outreach to the OpinionsQA / SubPOP / GlobalOpinionQA author
   teams.** They are the natural early citers; if they have not yet cited
   us, ask why directly.

---

## What good looks like at 90 days

The version of this that worked:

> 2026-08-12 closeout: 4.5 weighted citation points. 1 S-tier (citation in
> a NeurIPS D&B accepted-paper preprint), 2 A-tier (Latent Space podcast
> episode mentioning SynthBench, One Useful Thing essay quoting the
> conditioning-asymmetry finding), 3 B-tier (Greenbook profile, Synthetic
> Users blog post citing their SynthBench score, a practitioner-blog
> replication post on Substack). 5 vendor submissions to the public
> board. Stanford CRFM links to us from their benchmark index. Wesley's
> wesley@dataviking.tech inbox shows the first three "we'd like to cite
> SynthBench in our forthcoming paper, may we?" emails — the leading
> indicator that SynthBench has entered the academic citation graph.

That outcome is the "authoritativeness flywheel" going. From there, the
2026-Q3 report writes itself.

---

*Source: `docs/distribution/citation-seeding-plan-2026-Q2.md`. Owner:
Wesley. Window closes 2026-08-12. Retrospective in the 2026-Q3 quarterly
report.*
