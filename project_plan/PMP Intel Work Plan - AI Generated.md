# PMP Intel: Build Workflow & Architecture

## What You're Building

A **Prospect Marketing Intelligence Platform** that:
1. Takes an industry/niche as input and discovers prospect companies
2. Researches each company deeply across multiple data sources
3. Scores and analyzes their marketing position (creative, budget, growth, storytelling)
4. Stores everything in a persistent database
5. Renders the three HTML views you've already designed (Industry Sweep grid, Company Detail, Creative Strategy Analysis)
6. Generates personalized outreach emails
7. Tracks prospects through a CRM pipeline

---

## Part 1: How Claude Code Orchestrates This

The app runs entirely inside **Claude Code's ReAct agent loop**. You describe everything in markdown. The agent reads your skill files, spawns subagents, calls tools, and writes results to the database. Here is the execution model:

```
You type a command (e.g., "run industry sweep for luxury outdoor apparel")
  → Claude reads CLAUDE.md (app rules and routing)
  → Claude invokes the matching skill (pmp-industry-sweep)
  → Skill spawns research subagents (parallel, one per company)
  → Subagents use WebSearch + WebFetch + MCP tools
  → Results flow to analysis subagents
  → Analysis writes to SQLite database via db-manager skill
  → HTML renderer generates the sweep grid
  → Browser opens the report
```

Everything persists. Next session, Claude reads the database and continues where you left off.

---

## Part 2: Existing Assets You Can Use Immediately

### Existing Custom Skills (you already have these)

| Skill | Use in PMP Intel |
|---|---|
| `stock-analyzer-fundamental` | Analyze publicly traded prospects (revenue, margins, growth trajectory) |
| `stock-analyzer-sentiment` | Read market sentiment and news tone around a prospect |
| `wiki-manager` | Maintain a living knowledge base of industries and companies researched |

### Built-in Claude Code Tools (always available)

| Tool | Role |
|---|---|
| `WebSearch` | Find companies, news, ad spend signals, content strategy signals |
| `WebFetch` | Scrape company websites, social profiles, landing pages |
| `Agent` (subagent spawner) | Run parallel company research — one subagent per company |
| `Bash` | SQLite database operations, HTML file generation |
| `Read / Write / Edit` | Manage skill files, HTML templates, database schema |
| `TaskCreate / TaskUpdate` | Track sweep progress across multiple companies |
| `CronCreate` | Schedule weekly sweeps and re-analysis |

### Built-in Claude Code Skills (available via `/skill`)

| Skill | Use |
|---|---|
| `schedule` | Automate recurring sweeps (e.g., re-score industry every Monday) |
| `loop` | Iterate over a company list until sweep is complete |
| `update-config` | Wire up MCP servers, set permissions for tools |
| `init` | Generate CLAUDE.md — your first step |
| `claude-api` | If you later want to expose PMP Intel as an API endpoint |

---

## Part 3: Custom Skills You Need to Build

These are all **markdown files** in `~/.claude/skills/`. Each is a SKILL.md that Claude reads and executes. You describe what to do in natural language; Claude does it.

### Skill 1: `pmp-industry-sweep`

**Trigger:** "Run a sweep for [industry/niche]"

**What it does:**
- Queries WebSearch for top companies in the niche
- Filters by configurable criteria (size, geography, ad activity)
- Spawns one research subagent per company (parallel)
- Aggregates scores and writes to database
- Calls `pmp-html-renderer` to produce the Industry Sweep grid

### Skill 2: `pmp-company-analyzer`

**Trigger:** "Analyze [company name]" or called by `pmp-industry-sweep`

**What it does:**
- Researches company via WebSearch + WebFetch (website, LinkedIn, social, press)
- Calls `stock-analyzer-fundamental` if publicly traded
- Computes the 5 sub-scores: Creative, Budget, Growth, Storytelling, Opportunity
- Writes structured record to database
- Produces all sections: Overview, Ad Spend, Performance Metrics, Funnel Architecture, Creative Strategy Analysis, Storytelling Diagnostic

### Skill 3: `pmp-creative-analyzer`

**Trigger:** Called by `pmp-company-analyzer`

**What it does:**
- Scrapes company's website, YouTube, Instagram, LinkedIn, Meta Ad Library
- Classifies content into Video/Static/Carousel/Other
- Identifies top-performing themes (Winner Signals)
- Maps strengths vs. gaps
- Returns Creative Strategy Analysis section data

### Skill 4: `pmp-db-manager`

**Trigger:** Called internally by all other skills

**What it does:**
- Reads/writes the SQLite database
- Manages three tables: `prospects`, `analyses`, `outreach`
- Handles CRM stage updates (Lead → In-Research → Contacted → Active)
- Returns data for HTML rendering

### Skill 5: `pmp-html-renderer`

**Trigger:** Called by sweep/analysis skills, or "Show me the sweep for [industry]"

**What it does:**
- Reads analysis data from database
- Renders the three HTML views using your visual schema
- Opens in browser
- Exports CSV on request

### Skill 6: `pmp-outreach-composer`

**Trigger:** "Write outreach for [company]" or "Generate email for prospects in [stage]"

**What it does:**
- Reads company analysis from database
- Identifies the 2-3 most compelling hooks (their gaps vs. your services)
- Writes personalized email/LinkedIn message
- Stores draft in database under that prospect
- Optionally schedules send via email MCP

### Skill 7: `pmp-orchestrator`

**Trigger:** "Run PMP Intel for [industry]" — the master entry point

**What it does:**
- Calls `pmp-industry-sweep`
- Monitors Task progress across all subagents
- On completion, calls `pmp-html-renderer`
- Logs run to `wiki-manager` knowledge base
- Schedules follow-up re-analysis via `schedule` skill

---

## Part 4: MCP Servers to Configure

MCP servers give Claude access to external data. You configure these in `~/.claude/settings.json` using the `update-config` skill — no code needed.

### Priority MCP Servers (configure in Phase 1)

| MCP Server               | Data It Provides                                      | How to Get It                                                         |
| ------------------------ | ----------------------------------------------------- | --------------------------------------------------------------------- |
| **Brave Search**         | Web search with fresh index                           | `npx @modelcontextprotocol/server-brave-search` — needs Brave API key |
| **Playwright/Puppeteer** | Dynamic page scraping (social media, Meta Ad Library) | `npx @playwright/mcp`                                                 |
| **SQLite**               | Direct database read/write from Claude                | `npx @modelcontextprotocol/server-sqlite`                             |
| **Filesystem**           | Structured file access for HTML output                | `npx @modelcontextprotocol/server-filesystem`                         |

### Phase 2 MCP Servers (add when you reach outreach phase)

| MCP Server | Use |
|---|---|
| **Gmail / SendGrid** | Send outreach emails directly from Claude |
| **LinkedIn** | Prospect research, connection status |
| **Apollo.io / Hunter.io** | Contact data enrichment |
| **Clearbit** | Company firmographic data (revenue estimates, headcount) |

---

## Part 5: Database Schema (Outline — you will specify the full schema)

Three core tables. You will define the exact fields, and I'll build the `pmp-db-manager` skill around them.

```
prospects        — one row per company (name, domain, industry, CRM stage, scores)
analyses         — one row per analysis run (linked to prospect, all section data as JSON)
outreach         — one row per message (linked to prospect, draft text, sent status, response)
```

The database file lives at `~/Projects/Claude CLI/PMP Intel/pmp_intel.db`. SQLite is ideal — no server to manage, fully accessible via the SQLite MCP and Bash tool.

---

## Part 6: The Action Plan — Initialization to Scale

### Phase 0: Project Foundation (Session 1 — ~2 hours)

```
1. cd to project directory in Claude CLI
2. Run /init → generates CLAUDE.md (app identity, routing rules, tool permissions)
3. Run /update-config → add SQLite MCP, Brave Search MCP, Filesystem MCP
4. Run /fewer-permission-prompts → reduce approval friction for Bash + WebSearch
5. Define your prospect database schema (you describe in natural language, I write the schema)
6. Define your HTML display schema (you describe in natural language, I write the templates)
```

### Phase 1: First Custom Skill — Company Analyzer (Session 2 — ~3 hours)

```
1. Build pmp-company-analyzer SKILL.md in Claude CLI
2. Test: "Analyze Taylor Guitars" → verify all 5 sections generate correctly
3. Build pmp-db-manager SKILL.md
4. Connect analyzer output to database
5. Build pmp-html-renderer SKILL.md for Company Detail view
6. Verify: analysis runs → saves to DB → HTML opens in browser
```

### Phase 2: Industry Sweep (Session 3 — ~2 hours)

```
1. Build pmp-industry-sweep SKILL.md
2. Test: "Run a sweep for acoustic guitar manufacturers" → should produce ~10 company cards
3. Build pmp-html-renderer extension for Industry Sweep grid view
4. Verify: sweep runs in parallel → all companies scored → grid renders with scores
```

### Phase 3: Creative Analysis (Session 4 — ~2 hours)

```
1. Build pmp-creative-analyzer SKILL.md
2. Integrate Playwright MCP for social scraping
3. Connect to pmp-company-analyzer pipeline
4. Test: Creative Strategy Analysis section fills in for Taylor Guitars
```

### Phase 4: Outreach (Session 5 — ~2 hours)

```
1. Build pmp-outreach-composer SKILL.md
2. Define your email voice/tone/offer in the skill file
3. Test: "Write outreach for Taylor Guitars" → personalized email references their specific gaps
4. Connect email MCP for delivery
```

### Phase 5: Orchestrator & Automation (Session 6 — ~2 hours)

```
1. Build pmp-orchestrator SKILL.md
2. Run: "Run PMP Intel for premium home furnishings" → full pipeline end-to-end
3. Use /schedule skill to set up weekly re-sweeps
4. Use /loop skill for batch outreach generation across all Contacted prospects
```

### Phase 6: Scale (Ongoing)

```
1. Add industry verticals one at a time (each is a new sweep run, same skills)
2. Add MCP servers as needed (Apollo for contact enrichment, LinkedIn for warm signals)
3. Use wiki-manager to build institutional knowledge base across all industries researched
4. Refine scoring rubrics in skill files based on conversion data
```

---

## Part 7: Working Method in Claude CLI

Every skill is built in one session using this pattern:

```
You: "Build the pmp-company-analyzer skill. Here is what it should do: [description]"
Claude: Writes ~/.claude/skills/pmp-company-analyzer/SKILL.md
You: "Test it on Taylor Guitars"
Claude: Runs the skill, shows results
You: "The Creative section is missing the competitor comparison. Add that."
Claude: Edits SKILL.md
```

For large schemas (like your full HTML templates or database schema), you can draft them in Obsidian as markdown, then paste into Claude CLI or point Claude to the file path.

The CLAUDE.md file at your project root acts as the app's "brain" — it tells Claude which skill to invoke for which command, what the database looks like, and what your services and voice sound like.

---

## Summary: What You Need to Build vs. What Exists

| Component | Status | How Built |
|---|---|---|
| Research (web search + scraping) | Exists (WebSearch + WebFetch + Playwright MCP) | Configure MCP |
| Financial analysis (public companies) | Exists (`stock-analyzer-fundamental`) | Already built |
| Knowledge base | Exists (`wiki-manager`) | Already built |
| Scheduling | Exists (`schedule` skill) | Already built |
| Company analyzer | **Build** | SKILL.md in CLI |
| Industry sweep | **Build** | SKILL.md in CLI |
| Creative analyzer | **Build** | SKILL.md in CLI |
| Database manager | **Build** | SKILL.md in CLI |
| HTML renderer | **Build** | SKILL.md in CLI |
| Outreach composer | **Build** | SKILL.md in CLI |
| Orchestrator | **Build** | SKILL.md in CLI |
| SQLite database | **Configure** | MCP + schema definition |
| Email delivery | **Configure** | Email MCP |

---

## Next Step

Run `/init` in Claude CLI inside your project directory, then provide:

1. **Your prospect database schema fields** — what data points matter most to you per company
2. **Your scoring rubric** — what makes a prospect a 9.2 vs. a 6.4 (what dimensions, what weights)

That gives Claude everything needed to build Phase 0 and Phase 1 in one session.
