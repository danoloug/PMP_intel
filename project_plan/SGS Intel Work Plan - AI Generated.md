# PMP Intel — Build Workflow & Architecture (Regenerated)

> Regenerated 2026-05-14 from `project_plan/` and `screen_shots/`.
> Source inputs: `PMP Intel Work Plan.md`, `SGS_Intel_Work_Plan.md`, `Peter McCabe Pictures.md`, and the three UI screenshots (`Industry Sweep Review.png`, `Company Sweep Review.png`, `Creative Strategy Analysis.png`).

---

## 1. What You're Building

**PMP Intel** is a prospect marketing intelligence platform for a marketing services business. It:

1. Takes an industry/niche as input and discovers prospect companies
2. Pulls raw data from many sources in parallel (website, YouTube, Meta Ad Library, Instagram, press, financials)
3. Interprets that raw data through multiple analytical lenses (creative mix, storytelling, funnel, ad spend, opportunity)
4. Scores each prospect and stores everything in a persistent database
5. Renders three HTML views you've already designed (Industry Sweep grid, Company Sweep Review detail, Creative Strategy Analysis)
6. Drafts personalized outreach emails grounded in the analysis
7. Tracks prospects through a CRM pipeline (Lead → In-Research → Contacted → Active)

**Hard constraint:** You write **no code** — every behavior is defined in markdown (SKILL.md files, CLAUDE.md, MCP config). The Claude Code ReAct agent orchestrates everything by composing skills, spawning subagents, and calling MCP tools. The only exception is small custom tools when no MCP or built-in tool can satisfy a need.

---

## 2. Architecture (Borrowed from SGS Intel, Translated to Pure Markdown)

The SGS Intel plan (in this same directory) is your existing intuition about how this should work. PMP Intel adopts the same proven separations, but expressed entirely as skills instead of Python modules:

| SGS Intel concept | PMP Intel equivalent |
|---|---|
| Python fetcher modules | **Fetcher skills** under `~/.claude/skills/pmp-fetch-*` |
| Python interpreter agents | **Interpreter skills** under `~/.claude/skills/pmp-interpret-*` |
| `orchestrator/run.py` | **`pmp-orchestrator` skill** using the `Agent` tool to fan out |
| `skills/claude_call.py` wrapper | Not needed — Claude is the runtime, not a callee |
| `memory/queries.py` | **`pmp-db-manager` skill** (sole path to SQLite) |
| `raw_data_pulls` table | `raw_data/<prospect>/<source>.json` files + DB pointer rows |
| ChromaDB vector store | Vector MCP server (Phase 6, optional) |
| Next.js UI | **`pmp-html-renderer` skill** producing static HTML opened in browser |
| `deploy.command` script | One Claude command invocation — no deploy artifact |

### Why fetcher / interpreter separation matters

Re-running an interpreter without re-fetching is the single highest-leverage capability of this architecture. You will revise scoring rubrics constantly. If fetching and interpreting are fused, every rubric tweak costs another full scrape. Keep them separate from day one.

### The execution model

```
User: "Run PMP Intel for [industry]"
  → Claude reads CLAUDE.md for routing
  → pmp-orchestrator skill fires
      → pmp-industry-sweep discovers ~10-20 prospects via WebSearch + Brave MCP
      → For each prospect, spawn one Agent (parallel):
          → Agent runs all fetcher skills in parallel:
              pmp-fetch-website, pmp-fetch-youtube, pmp-fetch-meta-ads,
              pmp-fetch-instagram, pmp-fetch-press, pmp-fetch-financials
          → Raw data written to raw_data/<prospect>/ + pointer rows in DB
          → Agent runs interpreter skills in parallel:
              pmp-interpret-creative, pmp-interpret-storytelling,
              pmp-interpret-funnel, pmp-interpret-ad-spend, pmp-interpret-opportunity
          → Each interpreter writes a structured analysis row to DB
      → pmp-db-manager computes composite scores
      → pmp-html-renderer produces the Industry Sweep grid
      → Browser opens; CRM stages persisted
```

Everything between sessions lives in SQLite + `raw_data/`. Next session begins by reading the DB, not the conversation.

---

## 3. The Three Canonical UI Views (from screenshots)

The HTML renderer must produce exactly these three views. Section-by-section breakdown:

### View 1 — Industry Sweep Review (grid)

- **Header bar:** "Story Gap Pictures BRAND FILM INTEL", Export CSV
- **Top metrics:** Total Prospects (26), Researched (17), Unanswered (9), Contacted (0), Active (0) — these are CRM stage counts
- **Left rail (CRM):**
  - "Discovery Sweep" search box with placeholder example ("e.g. luxury outdoor apparel")
  - "Run Phase 0 Sweep" yellow CTA
  - Filter chips: Luxury Outdoor, Craft Spirits, Boutique Hotels, Sustainable Apparel, Premium Pet, Health Tech, Specialty Coffee, DTC Furniture, +Add
  - "Prospect CRM" with List/Cards toggle
  - Scrollable list of prospects: name, niche tags, score (e.g. 9.2), one-line insight
- **Main panel:** scored card grid (e.g. Taylor Guitars 9.2 with KPIs and a quick narrative)

### View 2 — Company Sweep Review (detail)

- **Header:** Company name (Taylor Guitars), category & location (Guitar Manufacturing — El Cajon, CA — taylorguitars.com), "EXCEPTIONAL PROSPECT — PHASE 0 READY" tag
- **Composite score:** 9.2/10
- **Four sub-scores:** Creative (4.5), Budget (9.5), Growth (9.8), Story Day (9.8) — confirm exact label "Story Day" vs "Other Day" with user
- **Action buttons:** Researched, Open Full Report, Re-Research, Delete
- **Notes field:** free text with Save Notes
- **Expandable sections** (each collapsible):
  1. **Company Overview** — 4 KPIs (Annual Revenue $125M+, Employees 1,200+, Daily Production 700-900 guitars, Market Share ~40% US acoustic) + narrative + founder story + awards/distribution/category badges
  2. **Ad Spend Estimation**
  3. **Performance Metrics**
  4. **Funnel Architecture**
  5. **Creative Strategy Analysis** (see View 3)
  6. **Storytelling Diagnostic**

### View 3 — Creative Strategy Analysis

- **Header chip:** "← Company Profile" back link
- **Creative mix:** Four numeric tiles — Video % (70%), Static % (20%), Carousel % (10%), A/B Testing % (25%)
- **Theme table:** Theme | Share % | Description (e.g. Technical Education Authority — ~50% — "Two-Minute Tech series…")
- **Winner Signals** callout list (long-running top performers)
- **Two-column footer:** Strengths (left) | Weaknesses / Gaps (right)

---

## 4. Skill Catalog

### Existing skills usable as-is

| Skill | Use |
|---|---|
| `stock-analyzer-fundamental` | Financial analysis for publicly traded prospects |
| `stock-analyzer-sentiment` | News + market sentiment around a prospect |
| `wiki-manager` | Cross-session knowledge base (one wiki page per industry; one per high-value prospect) |

### Built-in Claude Code capabilities to lean on

| Capability | Role |
|---|---|
| `Agent` tool | Parallel fan-out — one subagent per prospect, one per fetcher within a prospect |
| `WebSearch` + `WebFetch` | Discovery + static page reads |
| `Bash` | SQLite operations, opening HTML in browser, file ops |
| `Read` / `Write` / `Edit` | Skill authoring, HTML template management |
| `Task*` tools | Progress tracking across multi-prospect sweeps |
| `CronCreate` | Recurring sweeps and re-analysis |
| `/skill-creator` | Primary authoring loop for every skill below |
| `/update-config` | MCP and permission wiring |
| `/fewer-permission-prompts` | Reduce approval friction |
| `/schedule` | Cron-managed recurring runs |
| `/loop` | Batch operations across the CRM |

### Custom skills to build (the seven core, plus fetcher/interpreter splits)

**Orchestration tier**

| Skill | Trigger | Responsibility |
|---|---|---|
| `pmp-orchestrator` | "Run PMP Intel for [industry]" | Master coordinator; calls sweep → research → render → log |
| `pmp-industry-sweep` | "Run a sweep for [industry/niche]" | Discovers prospects; fans out research subagents; aggregates |

**Fetcher tier (raw data only, never interpret)**

| Skill | Pulls |
|---|---|
| `pmp-fetch-website` | About / Founders / Mission / History / Case Studies pages |
| `pmp-fetch-youtube` | Channel inventory, top videos, transcripts (SCOUT / STANDARD / DEEP presets — 5 / 10 / 18 videos) |
| `pmp-fetch-meta-ads` | Active ads from Meta Ad Library — creative text, themes, activity level |
| `pmp-fetch-instagram` | Public captions, cadence, theme signals (no login) |
| `pmp-fetch-press` | News mentions, founder interviews, awards |
| `pmp-fetch-financials` | Public financials via `stock-analyzer-fundamental` if listed; else estimates |

**Interpreter tier (read raw data, never re-fetch)**

| Skill | Produces |
|---|---|
| `pmp-interpret-creative` | The Creative Strategy Analysis view (Video/Static/Carousel %, themes, winner signals, strengths, gaps) |
| `pmp-interpret-storytelling` | Storytelling Diagnostic section — narrative coherence, character/conflict/resolution presence |
| `pmp-interpret-funnel` | Funnel Architecture section — acquisition surfaces, conversion paths, leak points |
| `pmp-interpret-ad-spend` | Ad Spend Estimation — channel mix, monthly burn, efficiency signals |
| `pmp-interpret-opportunity` | Top 3 outreach hooks: their gap → your service → expected impact |

**Storage / rendering / outreach tier**

| Skill | Role |
|---|---|
| `pmp-db-manager` | Sole path to SQLite; CRM transitions; composite-score derivation; idempotent re-runs |
| `pmp-html-renderer` | Renders the three canonical views from DB; opens in browser; exports CSV |
| `pmp-outreach-composer` | Drafts personalized email/LinkedIn grounded in stored interpretations |

---

## 5. MCP Servers

Configure via `/update-config`. Until configured, skills that depend on a missing MCP should fail loudly.

**Phase 1 — research + storage**

| MCP | Why |
|---|---|
| Brave Search | Fresh web index for discovery |
| Playwright | Dynamic scraping (Instagram, Meta Ad Library, JS-rendered sites) |
| SQLite | Direct DB access for `pmp-db-manager` |
| Filesystem | Structured HTML output and `raw_data/` writes |
| YouTube Transcript (or yt-dlp wrapper) | Channel + transcript pulls for `pmp-fetch-youtube` |

**Phase 2 — outreach**

| MCP | Why |
|---|---|
| Gmail or SendGrid | Email delivery |
| LinkedIn | Prospect research, connection status |
| Apollo.io / Hunter.io | Contact enrichment |
| Clearbit | Firmographics (revenue, headcount estimates) |

**Phase 6 — optional**

| MCP | Why |
|---|---|
| ChromaDB or pgvector MCP | Semantic search across all prospects for "find me prospects most like Taylor Guitars" |

---

## 6. Database Schema (you specify the fields; structure shown below)

SQLite, file lives at the project root as `pmp_intel.db`. **`pmp-db-manager` is the only path through which other skills read or write.** No raw SQL anywhere else.

Suggested table set (you will refine):

```
prospects        — one row per company (id, name, domain, industry, geography, crm_stage,
                   composite_score, created_at, last_researched_at, notes)
analyses         — one row per analysis run (id, prospect_id, run_id, section, payload_json,
                   interpreter_name, interpreter_version, created_at, is_current)
raw_data         — pointers to raw fetcher output (id, prospect_id, source, file_path,
                   fetched_at, fetcher_version)
outreach         — one row per drafted/sent message (id, prospect_id, channel, tone,
                   draft_text, status, sent_at, response_text, response_at)
run_log          — every fetcher and interpreter invocation (id, run_id, skill, prospect_id,
                   started_at, duration_ms, status, error)
crm_events       — append-only stage transitions (id, prospect_id, from_stage, to_stage, reason, at)
```

**Conventions:**
- `is_current` on `analyses` flips off the previous interpretation for the same prospect+section when a new one is written, so the renderer always reads the latest.
- Re-running an interpreter does **not** create a new prospect row; it adds a new `analyses` row and flips the previous one's `is_current=false`.
- Composite score is computed by `pmp-db-manager` on write, not by individual interpreters.

---

## 7. Versioning & Phase Discipline (borrowed from SGS plan)

- Keep `VERSION` and `RUBRIC_VERSION` files at project root. Bump `VERSION` every build. Bump `RUBRIC_VERSION` only when scoring rubrics in a SKILL.md change.
- `analyses.interpreter_version` records which `RUBRIC_VERSION` produced that row. Old rows stay readable even after rubrics change.
- Every fetcher and interpreter logs to `run_log` — never silently fail. On failure, log error and return an empty payload with an `error` field; the orchestrator decides whether to proceed.
- Test every skill standalone before wiring it into the orchestrator. "Test on Taylor Guitars" is the canonical regression input.

---

## 8. The Phased Action Plan

### Phase 0 — Project Foundation (Session 1, ~2 hours)

1. `cd` into project directory, run `/init` → CLAUDE.md is written
2. Create `VERSION` (e.g. `0.1.0`) and `RUBRIC_VERSION` (e.g. `1.0`) files
3. Run `/update-config` → install MCPs: SQLite, Brave Search, Filesystem, Playwright, YouTube Transcript
4. Run `/fewer-permission-prompts` to reduce approval friction for routine reads
5. **You provide:** full DB schema fields (refine the template in §6) and the natural-language HTML schema for each of the three views (refine the breakdown in §3)
6. I build: `pmp-db-manager` SKILL.md + initial schema migration; reusable HTML templates referenced by the renderer

**Definition of done:** `pmp-db-manager` can create a prospect, list prospects, transition stages, and the empty `pmp_intel.db` exists. No skills depend on raw SQL.

### Phase 1 — One Prospect, End to End (Session 2, ~3 hours)

1. Build the six fetcher skills (`pmp-fetch-*`) — each testable standalone on Taylor Guitars
2. Build three interpreter skills first: `pmp-interpret-creative`, `pmp-interpret-storytelling`, `pmp-interpret-opportunity`
3. Build `pmp-company-analyzer` as a thin orchestrator that calls fetchers in parallel, then interpreters in parallel, writes via `pmp-db-manager`
4. Build `pmp-html-renderer` for the **Company Sweep Review** view only

**Definition of done:** running `"Analyze Taylor Guitars"` produces a populated detail view in the browser with all six sections filled.

### Phase 2 — Industry Sweep (Session 3, ~2 hours)

1. Build `pmp-industry-sweep` — discovery + fan-out via `Agent`
2. Extend `pmp-html-renderer` to produce the **Industry Sweep Review** grid view
3. Add the CRM left-rail interactions (stage counters, filters)
4. Add the remaining two interpreters: `pmp-interpret-funnel`, `pmp-interpret-ad-spend`

**Definition of done:** `"Run a sweep for acoustic guitar manufacturers"` returns ~10 cards with scores, each clickable into the detail view, all stored in DB.

### Phase 3 — Creative Strategy Analysis Polish (Session 4, ~2 hours)

1. Wire Playwright MCP into `pmp-fetch-meta-ads` and `pmp-fetch-instagram` for dynamic content
2. Refine `pmp-interpret-creative` until the Creative Strategy view matches the screenshot exactly (4 numeric tiles, theme table, winner signals, strengths/gaps columns)
3. Add the **Creative Strategy Analysis** view to the renderer

**Definition of done:** the Creative Strategy view for Taylor Guitars matches the reference screenshot in structure (numbers will vary by data).

### Phase 4 — Outreach (Session 5, ~2 hours)

1. Build `pmp-outreach-composer` — pulls top 3 hooks from `pmp-interpret-opportunity`, drafts email in chosen tone
2. Define your service offer + voice in the skill file (warm, direct, provocative, formal tones — same set as SGS plan)
3. Configure Gmail or SendGrid MCP
4. Add CRM transition: drafting → `Contacted` stage when send confirms

**Definition of done:** `"Write outreach for Taylor Guitars"` produces an email that references their specific gaps and your specific service.

### Phase 5 — Orchestrator & Automation (Session 6, ~2 hours)

1. Build `pmp-orchestrator` — the master entry point that wires the above into one command
2. Use `/schedule` to set up weekly re-sweeps of priority industries
3. Use `/loop` for batch outreach across all prospects currently in `Contacted` for >7 days
4. Wire `wiki-manager` to log each sweep as a wiki page

**Definition of done:** `"Run PMP Intel for premium home furnishings"` executes the full pipeline end to end without intervention.

### Phase 6 — Scale & Refine (Ongoing)

1. Add industry verticals one at a time (no new skills needed — same pipeline, new input)
2. Add Phase 2 MCPs as needed (Apollo, LinkedIn, Clearbit)
3. Refine rubrics in interpreter SKILL.md files; bump `RUBRIC_VERSION`; re-run interpreters on stored raw data (no re-fetching)
4. Optionally add a vector MCP and a `pmp-similar-prospects` skill for semantic prospect discovery
5. Optionally add a Market Scanner skill (per SGS Phase 7) — lightweight SCOUT-level pull on many candidates, ranked by similarity to your best existing prospects

---

## 9. Operating Rules

These are the invariants every skill must honor. They live in CLAUDE.md so future Claude sessions see them on every invocation.

1. **Markdown-first.** Before writing code, check whether a SKILL.md or an MCP can do the job.
2. **Fetchers never interpret.** Raw data only — JSON to disk, pointer rows in DB.
3. **Interpreters never re-fetch.** They read from `raw_data/` only. This makes rubric tuning cheap.
4. **All DB I/O through `pmp-db-manager`.** No raw SQL elsewhere.
5. **Persistence over context.** State lives in SQLite + `raw_data/`. Never assume conversation memory carries between sessions.
6. **Parallel by default.** Sweep fans out across prospects; within a prospect, fetchers run in parallel; interpreters also run in parallel after fetching completes.
7. **Composite scores are derived, not invented.** Interpreters emit sub-scores; `pmp-db-manager` composes them.
8. **CRM transitions are explicit and append-only.** Every stage change writes a `crm_events` row.
9. **Idempotent re-runs.** Re-analyzing a prospect updates `analyses` with a new `is_current=true` row; it does not duplicate the prospect.
10. **Reference screenshots are the spec for HTML.** When the screenshots in `screen_shots/` change, the renderer must follow.

---

## 10. What Exists vs. What You Build

| Component | Status | How |
|---|---|---|
| Discovery (web + MCP) | Exists | Configure Brave Search + WebSearch |
| Dynamic scraping | Exists | Configure Playwright MCP |
| Financial analysis | Exists | `stock-analyzer-fundamental` |
| Knowledge base | Exists | `wiki-manager` |
| Scheduling | Exists | `/schedule` skill |
| Database access | **Build** | `pmp-db-manager` SKILL.md + SQLite MCP |
| Six fetcher skills | **Build** | Six SKILL.md files |
| Five interpreter skills | **Build** | Five SKILL.md files |
| Company analyzer | **Build** | One SKILL.md, thin coordinator |
| Industry sweep | **Build** | One SKILL.md using `Agent` fan-out |
| HTML renderer | **Build** | One SKILL.md + three view templates |
| Outreach composer | **Build** | One SKILL.md + voice definition |
| Orchestrator | **Build** | One SKILL.md (master entry) |
| Email delivery | **Configure** | Gmail or SendGrid MCP |

---

## 11. Next Concrete Step

Open Claude CLI in the project directory and provide:

1. **Final DB schema fields.** Use the §6 template as a starting point — add/remove fields, lock in column types.
2. **Scoring rubric.** For each interpreter, what makes a 9.x vs a 6.x? Concrete benchmarks per sub-score.
3. **Confirm the fourth sub-score label.** The screenshot shows "Other Day" or possibly "Story Day" — pick one and I'll use it consistently.
4. **Confirm Phase 0 scope.** Build `pmp-db-manager` + initialize DB + scaffold HTML templates in Session 1, then move to fetchers in Session 2.

Once those four are settled, Phase 0 can complete in one session.
