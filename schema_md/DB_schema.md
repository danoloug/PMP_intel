# Story Gap Intel — Database Schema
# Natural language description for Claude Code CLI
# Paste this into Claude Code to define or regenerate the SQLite database

---

## Overview

The database is SQLite, stored locally at `~/Desktop/Projects/Lead_Research_Intel/sgs-intel/prospects.db`.
All reads and writes go through `memory/queries.py` — no inline SQL anywhere else in the app.
Every table uses an auto-incrementing integer primary key called `id`.
All timestamps are stored as ISO 8601 strings in UTC.

---

## Table 1: prospects

This is the master record for every brand being researched.

One row per company. Never deleted — archive instead by setting status to "archived".

Fields:
- id — primary key
- company_name — the brand name as entered by the user
- website_url — the brand's primary website
- instagram_handle — @handle without the @, nullable
- youtube_channel — full channel URL or handle, nullable
- industry — free text category (e.g. "outdoor gear", "DTC skincare")
- revenue_estimate — text range (e.g. "$1M–$5M"), nullable
- status — one of: "new", "researched", "contacted", "responded", "archived"
- outreach_stage — one of: "none", "drafted", "sent", "replied", "closed"
- prospect_score — integer 0–100, overall score from last deep dive
- story_gap_score — decimal 0–10, Muse framework story gap rating
- economic_viability_score — decimal 0–10, brand film ROI viability
- muse_people_score — decimal 0–10
- muse_plot_score — decimal 0–10
- muse_place_score — decimal 0–10
- muse_purpose_score — decimal 0–10
- notes — free text, user-editable field for personal observations
- created_at — timestamp when prospect was first added
- last_researched_at — timestamp of most recent deep dive
- app_version — the VERSION string active when last researched
- story_logic_version — the STORY_LOGIC_VERSION string active when last researched

---

## Table 2: raw_data_pulls

Stores the raw scraped data from every fetcher agent, exactly as returned.
Never overwritten — every run appends a new row. This lets us re-run interpreters
without re-scraping.

One row per fetcher per run.

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- source — one of: "website", "youtube", "meta_ads", "instagram", "press"
- run_id — UUID string grouping all fetchers from the same research run
- raw_json — the complete JSON blob returned by the fetcher, stored as TEXT
- fetcher_version — version string of the skill that produced this data
- pulled_at — timestamp
- status — one of: "success", "partial", "failed"
- error_message — null on success, error text on failure

---

## Table 3: youtube_videos

One row per YouTube video discovered for a prospect.
Populated by the YouTube fetcher agent using yt-dlp for discovery
and youtube-transcript-api for transcript text.

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

## Table 4: interpretations

Stores the output of every interpretation agent run against a raw data pull.
One row per interpreter per run. Multiple interpreters can run against the
same raw_data pull, each producing a separate interpretation record.

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- run_id — same UUID as the raw_data_pulls it was built from
- interpreter — one of: "muse_analyzer", "emotional_tone", "story_gap",
  "competitor_gap", "outreach_angle"
- result_json — the full structured output from the interpreter as JSON text
- story_logic_version — STORY_LOGIC_VERSION active when this ran
- created_at — timestamp
- token_count — integer, approximate tokens used for this call

---

## Table 5: reports

One assembled report per run. Built from selected interpretations.
Versioned — old reports are never deleted, just superseded by newer ones.

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- run_id — UUID matching the raw_data_pulls and interpretations used
- report_json — the full 10-section report as a JSON blob
- interpreters_used — comma-separated list of which interpreters contributed
- app_version — VERSION string at time of generation
- story_logic_version — STORY_LOGIC_VERSION at time of generation
- is_current — boolean, true for the most recent report per prospect
- created_at — timestamp

---

## Table 6: report_sections

The 10 sections that make up every report, stored individually
so sections can be selectively regenerated without rebuilding the whole report.

Sections in order:
1. company_overview — who they are, founding story, market position
2. ad_spend — Meta ad activity, spend signals, creative themes
3. performance — estimated revenue range, growth signals, market traction
4. funnel — how they acquire and convert customers
5. creative — visual identity, brand voice, content style
6. storytelling — how they currently tell their story, what's working
7. opportunities — the 3 highest-leverage story gap opportunities for brand film
8. agency_fit — why Story Gap Studio specifically is the right partner
9. offer — suggested engagement structure and investment framing
10. sources — all URLs and data sources used in the report

Fields:
- id — primary key
- report_id — foreign key to reports.id
- prospect_id — foreign key to prospects.id
- section_number — integer 1–10
- section_key — string slug matching the list above
- content_json — the section content as structured JSON
- created_at — timestamp

---

## Table 7: outreach

Stores every email draft and its history per prospect.
Multiple drafts allowed per prospect — versioned, not overwritten.

Fields:
- id — primary key
- prospect_id — foreign key to prospects.id
- report_id — foreign key to the report this draft was based on, nullable
- subject_line — email subject
- body_text — plain text version of the email body
- tone — one of: "warm", "direct", "provocative", "formal"
- status — one of: "draft", "approved", "sent", "replied"
- sent_at — nullable timestamp
- replied_at — nullable timestamp
- reply_summary — brief text note about what the reply said, nullable
- created_at — timestamp

---

## Table 8: run_log

An append-only log of every agent execution.
Used for debugging, cost tracking, and audit trail.

Fields:
- id — primary key
- run_id — UUID grouping all agents in a single research run
- prospect_id — foreign key to prospects.id
- agent_name — the name of the skill or agent that ran
- status — one of: "started", "success", "failed", "skipped"
- error_message — null on success
- duration_seconds — how long the agent took
- token_input — integer, tokens sent
- token_output — integer, tokens received
- model_used — e.g. "claude-sonnet-4-6" or "claude-opus-4-7"
- created_at — timestamp

---

## Key Rules

1. No inline SQL anywhere except memory/queries.py
2. Raw data is never overwritten — always append new rows
3. Reports are versioned — set is_current=false on old, true on new
4. Every agent run writes to run_log regardless of success or failure
5. Prospect status and scores are updated after every successful report assembly
6. The run_id UUID is generated once at orchestration start and passed to all agents
