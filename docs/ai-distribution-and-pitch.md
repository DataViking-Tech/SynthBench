# DataViking — AI Distribution Surfaces + Umbrella Elevator Pitch

**Author:** crew/cpo
**Date:** 2026-04-19
**Companion to:** `ai-engineer-readiness.md`
**Scope:** Follow-up to mayor's two additional asks for AI Engineer Miami.

---

## Part 1 — Agent-Era Distribution Channels

Ranked by **reach ÷ effort for the AE Miami audience** (applied AI engineers, agent
builders, AI-native startups). Effort estimates assume one engineer who knows the codebase.

Products span SynthPanel (CLI + MCP server), SynthBench (CLI + public leaderboard site),
and Traitprint (hosted web app with API). Different channels map to different products.

### Tier S — Ship before Tuesday (table stakes + high ROI)

| # | Channel | Product | Effort | Reach | Why now |
|---|---------|---------|--------|-------|---------|
| 1 | **MCP Registry (GitHub + Anthropic directories)** | SynthPanel | ~2h | Very high | Server already exists (`synthpanel mcp-serve`). Listing is a metadata PR. Not being listed on Monday reads as "not serious about MCP" to an Anthropic-heavy audience. **TABLE STAKES.** |
| 2 | **Hugging Face Space (benchmark viewer)** | SynthBench | 1 day | Very high | Every credible eval benchmark lives on HF Spaces (HELM, MMLU, HumanEval). A drive-by researcher expects to find SynthBench there. Gradio wrapper around leaderboard.json + a "run the core suite" button. **TABLE STAKES.** |
| 3 | **Hugging Face Dataset (scored results)** | SynthBench | half day | High | Publish `leaderboard-results/` as a versioned HF dataset. Free citation path for researchers. Pairs with #2. |
| 4 | **Papers With Code listing** | SynthBench | 2h | Mid-high | Benchmark metadata + leaderboard mirror. Table-stakes for the research-leaning slice of the audience. |
| 5 | **Claude Code skill pack** — `/synthpanel-run`, `/synthbench-submit`, `/traitprint-profile` | All three | 1 day for three skills | High | Anthropic-heavy audience runs Claude Code. A ready-made skill they can `plugin install` during the demo is a conversion engine. **Differentiator** — few vendors have shipped skills yet. |

**Tier S bundle: ~3 engineer-days total. Ship all five before Monday EOD.**

### Tier A — Ship within 2 weeks (high differentiator value)

| # | Channel | Product | Effort | Reach | Notes |
|---|---------|---------|--------|-------|-------|
| 6 | **Composio tool listing** | SynthPanel | 1-2 days | Mid-high | Composio aggregates tools for LangChain/CrewAI/Autogen. One listing unlocks multiple frameworks. |
| 7 | **LangChain tool package** (`langchain-synthpanel`) | SynthPanel | 1 day | High | Thin wrapper over MCP tools. Publish to PyPI + LangChain Hub. |
| 8 | **CrewAI tool package** (`crewai-synthpanel`) | SynthPanel | 1 day | Mid | Same wrapper shape; separate import path. |
| 9 | **Cursor / Windsurf / Zed MCP visibility** | SynthPanel | 0 incremental | High | All three consume MCP; once #1 ships, this is free. Add one paragraph + screenshot to README. |
| 10 | **ChatGPT Custom GPT — "SynthPanel Focus Group"** | SynthPanel | 2-4h + hosted action endpoint | Mid (decaying) | GPT Store discoverability has softened, but the ChatGPT install base is still massive. Low-lift hedge. |

### Tier B — Ship within 1 quarter (steady background investment)

| # | Channel | Product | Effort | Reach | Notes |
|---|---------|---------|--------|-------|-------|
| 11 | **n8n community node** | SynthPanel | 2 days | Mid | No-code automation crowd. Template: "Slack thread → SynthPanel focus group → Notion doc". |
| 12 | **Zapier / Make connectors** | SynthPanel / Traitprint | 3-5 days each | Mid | Higher reach than n8n for non-technical buyers. Traitprint is the stronger fit here (HR/recruiting workflows). |
| 13 | **Hugging Face Space for Traitprint demo** | Traitprint | 1 day | Mid | Low stakes — primarily an SEO/discovery play. |
| 14 | **dstack / Replicate** | None | N/A | N/A | Poor fit. These host inference models, not eval pipelines or web apps. Skip. |
| 15 | **VS Code extension** | None | N/A | Low | Nothing in the portfolio is an editor-time tool. Skip. |
| 16 | **Anthropic Skills catalog (plugins)** | All three | 2 days (pairs with #5) | Mid-high | Once Claude Code skills exist, submit to catalog. Pending Anthropic's published process. |

### Tier C — Speculative / watch

| # | Channel | Product | Effort | Reach | Notes |
|---|---------|---------|--------|-------|-------|
| 17 | **AWS Bedrock Agents / Azure AI Agent Service** | SynthPanel | 1-2 weeks each | Mid (enterprise) | Only if an enterprise design partner materializes. |
| 18 | **Salesforce AgentForce / MuleSoft Anypoint** | Traitprint | 2-3 weeks | Mid (HR tech) | Only if HR-tech is a target vertical. |
| 19 | **ElevenLabs / Deepgram agent marketplaces** | SynthPanel | Unknown | Low-mid | Voice-agent angle — real only if SynthPanel ships a voice persona mode. |
| 20 | **arXiv paper + NeurIPS/ICML workshop submission** | SynthBench | 2-4 weeks + review cycle | Enormous long-term | Wrong time horizon for Tuesday, right time horizon for a Q3 credibility play. |

### Recommended ship order for the week

**Monday (EOD goal — 4 of 5 Tier S shipped):**
1. MCP Registry listing for SynthPanel (2h)
2. Papers With Code listing for SynthBench (2h)
3. Claude Code skill pack — `/synthpanel-run` + `/synthbench-submit` (1 day)
4. Hugging Face Space — SynthBench leaderboard viewer (1 day, parallelizable)

**Tuesday (demo day):** Tier S #3 (HF Dataset) if capacity. Demo-safe.

**Week 2-3:** Tier A (Composio + LangChain + CrewAI packages).

**Demo narrative unlock:** Tier S #1 and #5 let the demo include *"install the
SynthPanel MCP in Claude Code right now — one command, try it with me"* — a
conversion-maximizing live interaction this audience will remember.

### What NOT to chase

- **ChatGPT Plugins (legacy)** — deprecated path. Custom GPTs only.
- **Slack / Discord bots** — low ROI for this audience; they'll come to you.
- **Fine-tuning-platform partnerships** — wrong layer; our products don't need fine-tuning.
- **NPM packages** — no JS surface worth exposing today. Skip until there's a SynthPanel-node client worth publishing.

---

## Part 2 — DataViking Umbrella Elevator Pitch

### Who Wesley Johnson is (for pitch grounding)

From https://traitprint.com/wesley-johnson:
- **Background:** Analytics Engineer and Data Engineer by training (Airflow, dbt,
  Redshift, BigQuery, Databricks, Spark, Python, SQL — all rated 5/5). Senior
  Manager, Data Analytics & Development at Peloton (2023–2025); scaled team 0→7,
  stakeholder coverage 5→50+, led the Redshift→BigQuery migration, mentored 3
  engineers to Staff+.
- **Disposition:** "Data-Driven Decision Making", "Root Cause Analysis", "Technical
  Leadership" — all 5/5 soft skills. Story pattern on Traitprint repeatedly shows
  psychological-safety-forward, distributed-ownership leadership plus rigorous
  data instincts.
- **Founder era:** DataViking Technologies since 2026-01-15. Shipped fintech
  optimization (trading-card price tracking + ML rec engine), a Steam game on
  Godot, and SwipeMatch (AI portfolio + job matching, now Traitprint). Narrative
  on his profile frames him as running "agent-driven development" as de facto
  studio head across multiple domains.

**The human thread:** Wesley is a *data engineer who grew into a people leader*.
The three products are all about **turning humans into honest, measurable data** —
and that is the pitch.

### Three candidate pitches (30 seconds each)

---

#### Pitch A — "Honest human proxies for AI" (trust angle)

> "DataViking builds the trust layer for any AI product that makes claims about
> people. **Traitprint** turns a résumé into a rigorous professional profile with
> skill-level evidence. **SynthPanel** runs synthetic focus groups you can
> actually ship product decisions on. **SynthBench** measures, against real human
> survey data, whether those synthetic people match reality — or whether your
> model is just giving you trendslop. Represent real people, simulate
> populations, verify the fidelity. Three products, one mission: AI that tells
> the truth about humans."

*Strengths:* Lands the "trust" word first; works well with the Berkeley / HBR
trendslop framing SynthBench already uses; ties to the adversarial-robustness
posture.
*Weaknesses:* "Trust layer" is crowded terminology; slightly abstract.

---

#### Pitch B — "The measurable human" (measurement angle) — **RECOMMENDED**

> "Every AI product now makes assumptions about humans — what they'd choose,
> what they'd think, what they're qualified for. **DataViking makes those
> assumptions measurable.** **Traitprint** quantifies professional identity into
> structured skill evidence. **SynthPanel** generates synthetic user populations
> for research, product, and hiring decisions. **SynthBench** scores, against
> real population data, how well those populations match the humans they claim
> to represent. We built the ground truth so your AI doesn't have to guess.
> **Three products, one primitive: the measurable human.**"

*Strengths:* Crisp three-beat structure (represent / simulate / measure); "the
measurable human" is a **memorable phrase** a listener can repeat at dinner;
directly answers the AE Miami audience's skepticism ("where's the measurement?");
aligns with WJ's analytics-engineer identity — "data-driven decision making" is
literally his stated 5/5 soft skill; each product maps cleanly to a verb
(quantify / generate / score); scales to a 60-second version by adding one
example per product.
*Weaknesses:* "The measurable human" lands slightly clinical — softer in warm
social contexts than in technical ones. Offset by framing the benefit in human
terms ("your AI doesn't have to guess").

---

#### Pitch C — "Synthetic UXR that leadership will sign off on" (practitioner angle)

> "DataViking turns 'what would users think?' from a hunch into data. **SynthPanel**
> lets your team run a 500-person focus group in ten minutes. **SynthBench**
> proves — with real Pew-panel data — that those synthetic respondents are
> actually representative, or flags them when they aren't. **Traitprint** does
> the same job for professional identity in hiring and talent decisions. It's
> the decision infrastructure for AI-first teams that refuse to ship on vibes.
> Measurable synthetic humans, for every decision that used to need a real room."

*Strengths:* Punchy and concrete; clear buyer personas (UXR, hiring, product);
the "refuse to ship on vibes" line is quotable; Traitprint's hiring-adjacent use
case slots in naturally.
*Weaknesses:* Buries Traitprint (gets one sentence at the end, feels bolted-on);
overclaims Phase-2 scope (open-ended themes aren't in P_dist yet); "refuse to
ship on vibes" slightly polarizing for conservative enterprise buyers.

---

### Recommendation: **Pitch B.**

**Why:**

1. **It survives the room.** AE Miami attendees have heard every "trust layer"
   and "AI-native X" pitch this year. "The measurable human" is fresh linguistic
   territory and forces the listener to slow down enough to remember it.
2. **It maps 1:1 to the three products** without awkwardness. Each product owns
   one verb (quantify / generate / score) and occupies one layer (identity /
   synthesis / verification). A listener who asks "what does Traitprint actually
   do?" after the pitch gets an easy answer.
3. **It scales up and down.** 30 seconds as written. 15 seconds: drop the
   examples, keep the three-product structure and the closing line. 60 seconds:
   add one concrete outcome per product.
4. **It reinforces SynthBench's existing narrative.** The Berkeley-hardened,
   trendslop-measuring posture already on the site is the proof point for this
   pitch — the pitch and the product page tell the same story in the same
   language.
5. **It fits Wesley's own voice.** Per his Traitprint profile, WJ is a
   *measurement-first* operator (50% pipeline fidelity, 60% cycle-time
   reduction, 0→7 team, 5→50+ stakeholders — all Traitprint stories lead with
   numbers). "Make assumptions measurable" is a pitch he will deliver authentically
   rather than performatively.

### One-line reduction (for bio / LinkedIn / booth signage)

> **DataViking Technologies — tools for the measurable human.
> Traitprint. SynthPanel. SynthBench.**

### Founder one-liner (for Wesley to use in 1:1 intros)

> *"I'm Wesley — I run DataViking. We build three products that make the humans
> inside AI systems measurable — professional identity, synthetic populations,
> and the benchmark that verifies both."*

### Rejected framings (and why)

- *"We're building the open evaluation stack for human-AI interaction."* — too
  academic, and SynthPanel is a product not an eval.
- *"DataViking is the Vercel of synthetic research."* — over-analogized, borrows
  credibility it shouldn't need.
- *"We make LLMs honest."* — correct spirit but LLM-providers will read it as
  an insult and it boxes out the Traitprint product.

---

## Deliverables checklist

- [x] Readiness assessment (`ai-engineer-readiness.md`, shipped)
- [x] AI distribution ranking (this doc, Part 1)
- [x] Elevator pitch candidates + recommendation (this doc, Part 2)
- [ ] Pending: re-run `synthpanel prompt` with API key and append raw responses
      to the readiness doc (blocker: no provider key in crew/cpo env)

*End.*
