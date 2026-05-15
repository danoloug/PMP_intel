# PMP Intel — Database Schema
# Natural language description for Claude Code CLI
# Paste this into Claude Code to define or regenerate the SQLite database

---

## Overview

The database is SQLite, stored locally at
`/Users/dano/Projects/Claude_CLI/PMP_Intel/pmp_intel.db`
(also addressed by the `pmp-sqlite` MCP server defined in `.mcp.json`).

All reads and writes go through the `pmp-db-manager` skill, which uses the
SQLite MCP server — no other skill issues raw SQL. There is no Python
`queries.py`; this is a markdown-orchestrated app.

Every table uses an auto-incrementing integer primary key called `id`.
All timestamps are ISO 8601 strings in UTC (`strftime('%Y-%m-%dT%H:%M:%fZ','now')`).

Scoring model: the four sub-scores (Creative / Budget / Growth / Other Day)
come from the analyzers. The composite score (0–100) is **derived** by
`pmp-db-manager` on write — never invented by an analyzer.

CRM pipeline: `lead → in_research → contacted → active`, plus `archived`.
Stage transitions are explicit and never skipped silently:
- `lead → in_research` when a sweep/analysis begins
- `in_research → contacted` when outreach is sent
- `contacted → active` when a reply lands

---

## Table 1: prospects

Master record for every company. One row per company. Never deleted —
archive instead by setting `crm_stage` to `archived`. Re-analysis updates
the existing row (and appends new `analyses`/`reports` rows); it never
creates a duplicate prospect.

Fields:
- id — primary key
- company_name — brand name as entered by the user (required)
- website_url — primary website, nullable
- instagram_handle — handle without the @, nullable
- youtube_channel — channel URL or handle, nullable
- industry — free text category (e.g. "acoustic guitar manufacturers")
- revenue_estimate — text range (e.g. "$1M–$5M"), nullable
- crm_stage — one of: "lead", "in_research", "contacted", "active", "archived"
- outreach_stage — one of: "none", "drafted", "sent", "replied", "closed"
- composite_score — integer 0–100, derived composite from last analysis
- creative_score — decimal 0–10, Creative sub-score
- budget_score — decimal 0–10, Budget sub-score
- growth_score — decimal 0–10, Growth sub-score
- other_day_score — decimal 0–10, Other Day sub-score
- notes — free text, user-editable observations
- created_at — timestamp when prospect was first added
- last_analyzed_at — timestamp of most recent analysis run
- app_version — VERSION string active when last analyzed
- scoring_logic_version — SCORING_LOGIC_VERSION active when last analyzed

---

## Table 2: raw_data_pulls

Raw scraped data from every fetcher, exactly as returned. Never overwritten —
every run appends a new row, so interpreters can re-run without re-scraping.
One row per fetcher per run.

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- source — one of: "website", "youtube", "meta_ads", "instagram", "press"
- run_id — UUID grouping all fetchers from the same research run
- raw_json — complete JSON blob returned by the fetcher, stored as TEXT
- fetcher_version — version string of the skill that produced this data
- pulled_at — timestamp
- status — one of: "success", "partial", "failed"
- error_message — null on success, error text on failure

---

## Table 3: youtube_videos

One row per YouTube video discovered for a prospect. Used by creative
analysis. Populated by the YouTube fetcher (yt-dlp for discovery,
youtube-transcript-api for transcripts).

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- video_id — YouTube video ID string (e.g. "dQw4w9WgXcQ")
- title — video title
- view_count — integer
- published_at — date string
- duration_seconds — integer, nullable
- transcript_text — full transcript as plain text, nullable
- transcript_summary — Claude-generated 2–3 sentence summary, nullable
- transcript_status — one of: "none", "pulled", "summarized", "failed"
- pull_preset — one of: "SCOUT" (5 videos), "STANDARD" (10), "DEEP" (18)
- pulled_at — timestamp

---

## Table 4: analyses

Output of every analyzer run against a raw data pull. One row per analyzer
per run. Multiple analyzers can run against the same raw_data pull, each
producing a separate analysis record.

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- run_id — same UUID as the raw_data_pulls it was built from
- analyzer — one of: "company_analyzer", "creative_analyzer", "ad_spend",
  "growth_signals", "competitor_gap", "outreach_angle"
- result_json — full structured output from the analyzer as JSON text
- scoring_logic_version — SCORING_LOGIC_VERSION active when this ran
- created_at — timestamp
- token_count — integer, approximate tokens used for this call

---

## Table 5: reports

One assembled report per run, built from selected analyses. Versioned —
old reports are never deleted, just superseded. Set `is_current = 0` on the
old report and `1` on the new one.

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- run_id — UUID matching the raw_data_pulls and analyses used
- report_json — full report as a JSON blob
- analyzers_used — comma-separated list of which analyzers contributed
- app_version — VERSION string at time of generation
- scoring_logic_version — SCORING_LOGIC_VERSION at time of generation
- is_current — boolean (0/1), true for the most recent report per prospect
- created_at — timestamp

---

## Table 6: report_sections

The sections that make up the Company Sweep Review, stored individually so
sections can be selectively regenerated without rebuilding the whole report.

Sections (section_number, section_key):
1. company_overview — who they are, founding story, market position
2. ad_spend_estimation — Meta ad activity, spend signals, creative themes
3. performance_metrics — revenue range, growth signals, market traction
4. funnel_architecture — how they acquire and convert customers
5. creative_strategy — creative-mix %, theme share, Winner Signals (Creative Strategy Analysis view)
6. storytelling_diagnostic — how they tell their story now; strengths/gaps
7. opportunities — the highest-leverage marketing opportunities
8. fit_assessment — why this marketing services business is the right partner
9. engagement — suggested engagement structure and investment framing
10. sources — all URLs and data sources used

Fields:
- id — primary key
- report_id — foreign key to reports.id
- prospect_id — foreign key to prospects.id
- section_number — integer 1–10
- section_key — slug from the list above
- content_json — section content as structured JSON
- created_at — timestamp

---

## Table 7: outreach

Every outreach draft and its history per prospect. Multiple drafts allowed —
versioned, not overwritten.

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- report_id — foreign key to the report this draft was based on, nullable
- subject_line — email subject (nullable for LinkedIn)
- body_text — plain text message body
- channel — one of: "email", "linkedin"
- tone — one of: "warm", "direct", "provocative", "formal"
- status — one of: "draft", "approved", "sent", "replied"
- sent_at — nullable timestamp
- replied_at — nullable timestamp
- reply_summary — brief note about what the reply said, nullable
- created_at — timestamp

---

## Table 8: run_log

Append-only log of every agent execution. Used for debugging, cost tracking,
and audit trail.

Fields:
- id — primary key
- run_id — UUID grouping all agents in a single research run
- prospect_id — foreign key to prospects.id
- agent_name — name of the skill or agent that ran
- status — one of: "started", "success", "failed", "skipped"
- error_message — null on success
- duration_seconds — how long the agent took
- token_input — integer, tokens sent
- token_output — integer, tokens received
- model_used — e.g. "claude-sonnet-4-6" or "claude-opus-4-7"
- created_at — timestamp

---

## Indexes

- idx_prospects_crm_stage on prospects(crm_stage)
- idx_raw_prospect_run on raw_data_pulls(prospect_id, run_id)
- idx_yt_prospect on youtube_videos(prospect_id)
- idx_analyses_prospect_run on analyses(prospect_id, run_id)
- idx_reports_prospect_current on reports(prospect_id, is_current)
- idx_sections_report on report_sections(report_id)
- idx_outreach_prospect on outreach(prospect_id)
- idx_runlog_run on run_log(run_id)

---

## Key Rules

1. No raw SQL outside `pmp-db-manager` (which uses the SQLite MCP server).
2. Raw data is never overwritten — always append new rows.
3. Reports are versioned — set is_current=0 on old, 1 on new.
4. Every agent run writes to run_log regardless of success or failure.
5. Composite score is derived by pmp-db-manager on write, never invented
   by an analyzer. Sub-scores come from the analyzers.
6. Prospects are never deleted — archive via crm_stage = 'archived'.
7. Re-analysis updates the existing prospects row and appends new
   analyses/reports rows; it never duplicates a prospect.
8. CRM stage transitions are explicit and never skipped silently.
9. The run_id UUID is generated once at orchestration start and passed
   to all agents.
