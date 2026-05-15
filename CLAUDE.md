# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Identity

**PMP Intel** is a strategic marketing analysis agentic app for the user's marketing services business. It researches prospective customers, scores their marketing position, stores findings in a persistent database, renders HTML reports, and generates personalized outreach.

This is **not a traditional codebase**. It is a markdown-orchestrated Claude Code application:

- The user does **not write code**. The user may only write small custom tools when no MCP server or built-in tool can satisfy a need.
- All behavior is defined in markdown: `CLAUDE.md` (this file), `SKILL.md` files under `~/.claude/skills/<skill-name>/`, and optional subagent definitions.
- Orchestration runs entirely inside the Claude Code ReAct loop. Skills compose by calling each other; subagents (spawned via the `Agent` tool) handle parallel work; MCP servers provide external data.
- Persistence is required across sessions — state lives in a local SQLite database, not in conversation context.

When in this project, **default to building or refining skills, not writing application code**.

## App Workflow (canonical execution model)

```
User command (e.g. "run industry sweep for luxury outdoor apparel")
  → Claude reads this CLAUDE.md for routing
  → Claude invokes the matching skill (e.g. pmp-industry-sweep)
  → Skill discovers companies via WebSearch + MCP
  → Skill spawns one research subagent per company (parallel via Agent tool)
  → Each subagent calls pmp-company-analyzer → pmp-creative-analyzer
  → Results written to SQLite via pmp-db-manager
  → pmp-html-renderer produces the report view
  → Browser opens the HTML; CRM stage updates persisted
```

## Skill Catalog

### Custom skills to build for this project (each is a markdown SKILL.md)

| Skill | Triggered by | Purpose |
|---|---|---|
| `pmp-orchestrator` | "Run PMP Intel for [industry]" | Master entry point; coordinates sweep → analyze → render → log |
| `pmp-industry-sweep` | "Run a sweep for [industry/niche]" | Discovers prospect list; fans out research subagents; aggregates scores |
| `pmp-company-analyzer` | "Analyze [company]" or called by sweep | Produces all sections of the Company Sweep Review |
| `pmp-creative-analyzer` | Called by company-analyzer | Produces the Creative Strategy Analysis section |
| `pmp-db-manager` | Called by all other PMP skills | Reads/writes SQLite; manages CRM stage transitions |
| `pmp-html-renderer` | Called by sweep/analyzer, or "Show me the sweep for [industry]" | Renders the three HTML views; opens in browser |
| `pmp-outreach-composer` | "Write outreach for [company]" | Generates personalized email/LinkedIn drafts grounded in stored analysis |

### Existing user skills usable as-is

- `stock-analyzer-fundamental` — fundamental analysis for publicly traded prospects
- `stock-analyzer-sentiment` — news/market sentiment for a prospect
- `wiki-manager` — knowledge base layer (use to log industries and notable prospects)

### Built-in Claude Code skills referenced by this project

- `/init` — generates/updates this file
- `/update-config` — wires MCP servers and permissions into `~/.claude/settings.json`
- `/fewer-permission-prompts` — reduces approval friction for routine read-only tools
- `/schedule` — recurring sweeps and re-analysis
- `/loop` — batch operations across prospect lists
- `/skill-creator` — primary tool for authoring new SKILL.md files in this project

## Required External Capabilities (MCP Servers)

Configure these via `/update-config` before running end-to-end. Until configured, skills that depend on them should fail loudly rather than silently degrade.

**Phase 1 (research + storage):**
- Brave Search MCP — fresh web index
- Playwright MCP — dynamic page scraping (social, Meta Ad Library)
- SQLite MCP — direct database access
- Filesystem MCP — structured HTML output

**Phase 2 (outreach):**
- Gmail or SendGrid MCP — email delivery
- LinkedIn / Apollo / Hunter / Clearbit MCP — contact and firmographic enrichment

## Three Canonical UI Views

The HTML renderer must produce these three views. The visual schema is defined by reference screenshots the user maintains in this project (Industry Sweep Review, Company Sweep Review, Creative Strategy Analysis). When those screenshots are present in this directory, read them before rendering or editing templates.

1. **Industry Sweep** — grid of scored company cards with left-side CRM pipeline (Lead → In-Research → Contacted → Active), export CSV
2. **Company Sweep Review** — single-prospect detail with KPIs, sub-scores (Creative / Budget / Growth / Other Day), and expandable sections: Company Overview, Ad Spend Estimation, Performance Metrics, Funnel Architecture, Creative Strategy Analysis, Storytelling Diagnostic
3. **Creative Strategy Analysis** — creative-mix percentages (Video / Static / Carousel / A/B), theme share table, Winner Signals, Strengths, Weaknesses/Gaps

## Database

- **Engine:** SQLite (file-based, no server)
- **Path:** `pmp_intel.db` at the project root (or as defined by the user)
- **Tables (logical — full schema to be defined by user):**
  - `prospects` — one row per company; identity, industry, CRM stage, latest composite score
  - `analyses` — one row per analysis run; full section payloads as JSON, linked to a prospect
  - `outreach` — one row per drafted/sent message; linked to a prospect

The `pmp-db-manager` skill is the only path through which other skills read or write the database. Do not let other skills issue raw SQL.

## Operating Rules

- **Markdown-first:** Before writing code, check whether a SKILL.md or an MCP server can do the job. Only write code when a custom tool is genuinely required, and keep such tools small and single-purpose.
- **Persistence over context:** Never rely on conversation memory for prospect data. Always read from and write to the database.
- **Subagents for fan-out:** When sweeping an industry, spawn one `Agent` per prospect in parallel. Do not serialize research that can run concurrently.
- **Composite scores are derived, not invented:** Sub-scores come from the analyzers; the composite is computed by `pmp-db-manager` on write.
- **CRM stage transitions are explicit:** A prospect moves Lead → In-Research when sweep begins, In-Research → Contacted when outreach is sent, Contacted → Active when a reply lands. Never skip stages silently.
- **Idempotent re-runs:** Re-analyzing a prospect should update its existing row (and append a new `analyses` row), not create duplicates in `prospects`.
- **Reference screenshots are the spec for HTML output.** When they exist in the project directory, read them before changing rendering logic.

## Common User Commands (after Phase 1 is built)

- `"Run PMP Intel for [industry]"` — full pipeline
- `"Analyze [company name]"` — single-company deep dive
- `"Show me the sweep for [industry]"` — re-render existing data
- `"Write outreach for [company]"` — generate personalized message
- `"Move [company] to Contacted"` — manual CRM stage transition
- `"Re-sweep [industry]"` — refresh all prospects in an industry

## Working Method

This project is built one skill at a time, in the Claude CLI, using `/skill-creator` to scaffold each SKILL.md. After scaffolding:

1. Test the skill on a known prospect (e.g. Taylor Guitars) or industry (e.g. acoustic guitar manufacturers).
2. Iterate the SKILL.md in place — no separate code review cycle.
3. When SKILL.md grows large, the user may edit it in Obsidian and reload.

The full phased action plan lives in `PMP Intel Work Plan - AI Generated.md` (regenerate if absent — Claude has the plan in project memory at `~/.claude/projects/-Users-dano-Projects-Claude-CLI-PMP-Intel/memory/`).

## What This Project Is Not

- Not a Python/JS/TS application — do not scaffold `package.json`, `pyproject.toml`, or similar.
- Not a web service — there is no server, no API surface, no deployment target beyond the user's machine.
- Not a one-shot script — every run must update persistent state usable by the next session.
