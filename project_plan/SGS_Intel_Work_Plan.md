# Story Gap Intel — Work Plan
# Migration from Flask v2.2.4 to Multi-Agent Architecture
# Natural language for Claude Code CLI

---

## What Exists Today

Story Gap Intel is a working Flask/SQLite app at:
`~/Desktop/Projects/Lead_Research_Intel/sgs-intel/`

Current version: v2.2.4 / Story Logic v1.2
Port: 5200
Python: Anaconda
Deploy: double-click `deploy.command` → unzips, copies templates, restarts Flask, opens Safari

What it does today:
- Takes a company name, runs a Claude API sweep with web search
- Generates a 10-section brand film intelligence report
- Stores prospects and reports in SQLite
- Shows reports in a browser UI (Obsidian/Champagne design)
- Pulls YouTube transcripts via yt-dlp + youtube-transcript-api
- Drafts outreach emails with tone controls
- Tracks outreach status per prospect

What it cannot do yet:
- Parallel data fetching (everything runs sequentially)
- Separate interpretation passes (Muse analysis is baked into one big Claude call)
- Semantic search across prospects (no vector store)
- Autonomous prospect discovery by market category
- Select which interpreters to run per prospect
- View multiple interpretation versions side by side

---

## What We Are Building

A multi-agent orchestrated version of Story Gap Intel with:
- Parallel fetcher agents (one per data source)
- Separate selectable interpretation agents
- Three-layer data storage: SQLite (structured) + raw JSON (re-runnable) + ChromaDB (semantic)
- Next.js UI (replaces Flask templates)
- Claude Code native ReAct agent as orchestrator (LangGraph added only if needed)
- All Claude calls routed through a single wrapper skill

The 10-section report, Story Gap scoring, and outreach email drafting all stay.
The Muse Storytelling Framework stays as the core analysis methodology.

---

## Folder Structure to Initialize

```
~/Desktop/Projects/Lead_Research_Intel/sgs-intel-v3/
├── VERSION
├── STORY_LOGIC_VERSION
├── deploy.command
├── orchestrator/
│   └── run.py                  # main entry point, manages state
├── agents/
│   ├── muse_analyzer.py
│   ├── emotional_tone.py
│   ├── story_gap.py
│   ├── competitor_gap.py
│   ├── outreach_angle.py
│   ├── report_assembler.py
│   ├── prospect_scorer.py
│   └── outreach_drafter.py
├── skills/
│   ├── claude_call.py          # single API wrapper, all models
│   ├── web_scraper.py
│   ├── youtube_puller.py       # yt-dlp + youtube-transcript-api
│   ├── meta_ads_puller.py
│   ├── instagram_puller.py
│   ├── press_puller.py
│   └── embedder.py             # ChromaDB read/write
├── memory/
│   ├── queries.py              # all SQLite read/write, no inline SQL elsewhere
│   ├── story_logic.md          # Muse framework prompt (port from v2.2.4)
│   └── prospects.db            # SQLite database
├── vector_store/
│   └── chroma/                 # ChromaDB local storage
└── ui/                         # Next.js frontend
    ├── package.json
    ├── pages/
    │   ├── index.js            # dashboard
    │   ├── prospect/[id].js    # report page
    │   └── email/[id].js       # email composer
    └── components/
```

---

## Phase 1 — Foundation (Do This First)

Goal: app scaffolded, database working, Claude can be called

Steps:
1. Create the full folder structure above
2. Create VERSION file containing "3.0.0"
3. Create STORY_LOGIC_VERSION file containing "1.2" (matching current v2.2.4)
4. Build `memory/queries.py` — all 8 database tables from DB_schema.md
   Initialize the SQLite database with all tables on first run
5. Build `skills/claude_call.py` — single wrapper function that:
   - Accepts model name, system prompt, user prompt, max_tokens
   - Defaults to claude-sonnet-4-6 for fetchers, claude-opus-4-7 for interpreters
   - Has retry logic: 3 attempts with exponential backoff on rate limit errors
   - Logs every call to run_log table (tokens in, tokens out, model, duration)
   - Never called directly from agents — always imported from this file
6. Port `memory/story_logic.md` from v2.2.4 — copy it exactly, no changes yet
7. Create a `deploy.command` script that:
   - Installs Python dependencies
   - Installs Node dependencies in /ui
   - Starts the Python orchestrator API on port 5200
   - Starts the Next.js dev server on port 3000
   - Opens Safari to localhost:3000

Verify Phase 1 complete: running `python orchestrator/run.py --test` should
initialize the database, write a test row, and confirm Claude API connection.

---

## Phase 2 — Fetcher Skills (Test Each Standalone)

Build each fetcher as a standalone Python script that can be run independently.
Every fetcher follows the same pattern:
- Takes a prospect dict as input (company_name, website_url, etc.)
- Returns a JSON-serializable dict of raw data only — no interpretation
- Writes raw data to raw_data_pulls table via queries.py
- Logs to run_log table
- On failure: logs error, returns empty dict with error key — never crashes

Build order:
1. `skills/web_scraper.py` — scrapes website_url for About, Founders, Mission, History,
   Case Studies pages. Returns all text as structured JSON by page section.
   Test standalone: `python skills/web_scraper.py --url "https://taylorguitars.com"`

2. `skills/youtube_puller.py` — uses yt-dlp for channel discovery (video IDs, titles,
   view counts), then youtube-transcript-api for transcripts.
   Supports SCOUT (5 videos) / STANDARD (10) / DEEP (18) presets.
   Writes to youtube_videos table and raw_data_pulls table.
   Test standalone: `python skills/youtube_puller.py --channel "@taylorguitars" --preset STANDARD`

3. `skills/meta_ads_puller.py` — calls Meta Ad Library API for active ads.
   Returns ad creative text, estimated activity level, content themes.
   Test standalone: `python skills/meta_ads_puller.py --brand "Taylor Guitars"`

4. `skills/instagram_puller.py` — scrapes public profile for captions, engagement signals,
   posting cadence, content themes. No login required — public data only.
   Test standalone: `python skills/instagram_puller.py --handle "taylorguitars"`

5. `skills/press_puller.py` — searches for news mentions, earned media, founder interviews,
   awards. Uses web search via Claude tool_use.
   Test standalone: `python skills/press_puller.py --brand "Taylor Guitars"`

6. `skills/embedder.py` — reads from and writes to ChromaDB vector store.
   Two functions: embed_text(text, metadata) and search_similar(query, n_results).
   Test standalone: `python skills/embedder.py --test`

After each fetcher is confirmed working standalone, wire it into orchestrator/run.py.
All fetchers run in parallel using Python's concurrent.futures.

---

## Phase 3 — Interpretation Agents

Each interpreter reads from raw_data_pulls (never re-scrapes) and produces
a structured JSON result stored in the interpretations table.

All interpreters use claude-opus-4-7 via skills/claude_call.py.
All read from memory/story_logic.md for the Muse framework context.

Build order:
1. `agents/muse_analyzer.py` — scores People, Plot, Place, Purpose 0–10 with evidence quotes
   Identifies which Muse Story Type the brand currently embodies
   Output: four scored dimensions + evidence + story type classification

2. `agents/story_gap.py` — identifies the 3 highest-leverage story gaps
   For each gap: what's missing, why it matters, what a brand film could deliver
   Output: three opportunity objects with gap, solution, and impact fields

3. `agents/emotional_tone.py` — analyzes dominant brand voice and emotional signals
   Output: primary tone, secondary tone, authenticity score, buyer emotion targets

4. `agents/competitor_gap.py` — how this brand's story differs from category peers
   Requires at least one other researched prospect in same industry to run
   Output: differentiation map, story positioning gaps, vulnerability signals

5. `agents/outreach_angle.py` — surfaces the single highest-leverage hook for cold email
   Output: primary angle, supporting evidence, suggested subject line hook

---

## Phase 4 — Synthesis and Orchestration

1. `agents/report_assembler.py` — reads selected interpretations, assembles 10-section report
   Takes a list of interpretation IDs to include (user selects which ran)
   Writes final JSON to reports table and report_sections table
   Sets is_current=true on new report, false on previous report for same prospect

2. `agents/prospect_scorer.py` — calculates overall score, story gap score, economic viability
   Updates prospect record in prospects table with new scores
   Writes scoring rationale to report JSON

3. `agents/outreach_drafter.py` — writes cold email using story gap and outreach angle results
   Supports four tones: warm, direct, provocative, formal
   Accepts free-text instruction for revision
   Writes to outreach table with tone tag

4. `orchestrator/run.py` — the main coordinator
   Entry points:
   - `run_research(prospect_id, interpreters=["muse", "story_gap"], preset="STANDARD")`
   - `run_interpreters_only(prospect_id, interpreters)` — re-runs without re-scraping
   - `run_email_draft(prospect_id, tone="warm", instruction=None)`
   
   Flow:
   a. Generate run_id UUID
   b. Run all fetchers in parallel → wait for all to complete
   c. Run selected interpreters in parallel → wait for all to complete
   d. Run report_assembler → prospect_scorer
   e. Update prospect record with new scores and last_researched_at
   f. Return report_id to UI

---

## Phase 5 — Next.js UI

Port the existing Obsidian/Champagne design system into Next.js.
Keep all the visual decisions already made — colors, typography, layout.

Pages to build:
1. Dashboard (pages/index.js) — card/list toggle, search, add prospect modal
2. Report page (pages/prospect/[id].js) — full 10-section report, YouTube panel,
   interpreter selector, version history drawer
3. Email composer (pages/email/[id].js) — tone selector, free-text instruction,
   regenerate controls, copy and mark-as-sent actions

The Next.js frontend calls the Python orchestrator via a local REST API.
The Python side exposes these endpoints on port 5200:
- GET /prospects — list all
- POST /prospects — add new
- GET /prospects/:id — get one with latest report
- POST /research/:id — run research (accepts interpreter list and preset)
- GET /reports/:id — get full report JSON
- POST /email/:id — generate or regenerate email draft
- GET /email/:id/history — list previous drafts

---

## Phase 6 — Data Migration

After the new app is working end-to-end with a test prospect:

1. Export all existing prospects from v2.2.4 prospects.db
2. Import company names, URLs, handles, status, outreach stage into new prospects table
3. Import existing phase2_data as a legacy report record (mark interpreter as "legacy_v2")
4. Do NOT import old reports as current — they're v2 format, mark as archived
5. Re-run deep dives on top 5 prospects to generate proper multi-agent reports

---

## Phase 7 — Market Scanner (Future / Sellable Feature)

After Phase 6 is stable:

1. Add a Market Scanner page to the UI
2. User defines a category (e.g. "DTC outdoor gear brands $1M–$10M revenue")
3. Press Agent + Web Scraper discover candidate brands via search
4. Each candidate runs a lightweight SCOUT-level fetch
5. ChromaDB embedder scores candidates by semantic similarity to your best existing prospects
6. Ranked queue presented to user — one-click to promote a candidate to full research

---

## Rules for Every Session

1. Bump VERSION on every build — no exceptions (3.0.0 → 3.0.1 → 3.0.2 etc.)
2. Bump STORY_LOGIC_VERSION only when story_logic.md content changes
3. Fetcher agents return raw data only — never interpret or score
4. All Claude API calls go through skills/claude_call.py — never direct
5. All database reads/writes go through memory/queries.py — never inline SQL
6. Fetchers run in parallel by default — use concurrent.futures
7. Every agent logs to run_log — never silently fail
8. Test each skill standalone before wiring into orchestrator
9. Claude Code builds — Peter directs in plain English, no code review expected

---

## Starting Point for Claude Code

When you begin a session, read these three files first:
- DB_schema.md — the complete data model in natural language
- UI_schema.md — every screen and component in natural language
- This file (SGS_Intel_Work_Plan.md) — the build phases and rules

Then confirm: which phase are we on, what was completed last session,
and what is the next concrete deliverable. Begin there.
