LEAD RESEARCH INTEL



Reconstruction Guide, Architecture Reference & Prompt Library

App v2.2.4  /  Story Logic v1.2  /  April 2026

1. What This App Does

Lead Research Intel (PMP Intel) is a Flask/SQLite CRM and prospect intelligence tool built for Peter McCabe Pictures — a premium brand film production company in Los Angeles. It finds, researches, and scores DTC brands that need brand film production, then generates full intelligence reports and personalized outreach emails.

The core workflow:

• Phase 1 Sweep: Claude searches the web for 12–15 real companies in a given niche, scores each on 4 dimensions, and saves them to the CRM.

• Phase 2 Deep Dive: A two-call pipeline pulls real local data (YouTube transcripts, Meta Ad Library, Apify social), then runs company intel and story analysis through Claude.

• Report: A full 10-section brand film intelligence report with storytelling diagnostic, opportunities, offer structure, and outreach email.

• Email Composer: Draft, tone-adjust, and send personalized cold outreach from the report data.

2. Tech Stack

Core

• Runtime: Python 3 (Anaconda)

• Web: Flask — port 5200, local Mac server

• Database: SQLite via instance/prospects.db

• AI Model: Anthropic claude-sonnet-4-20250514

• YouTube: yt-dlp + youtube-transcript-api

• Ads: Meta Ad Library public API (no auth required)

• Social: Apify API — optional, Instagram + TikTok (APIFY_API_KEY)

File Structure

pmp-intel/

 app.py                 — Flask app, all routes + data pipeline

 templates/

   index.html           — Dashboard, CRM list/card view, sweep UI

   report.html          — Full 10-section intelligence report

   email_composer.html  — Outreach email drafting page

 story_logic.md         — Muse Storytelling Framework (prompt knowledge base)

 VERSION                — App version (bump every build)

 STORY_LOGIC_VERSION    — SL version (bump only when story_logic.md changes)

 deploy.command         — Double-click to deploy + restart + open Safari

 instance/prospects.db  — SQLite database

 flask.log              — Flask output log

Environment Variables

# Required

export ANTHROPIC_API_KEY='sk-ant-...'

# Optional — enables real Instagram/TikTok data

export APIFY_API_KEY='apify_api_...'

# Add both to ~/.bash_profile

3. Database Schema

prospects table

id, company_name, genre, location, website, founder

prospect_score, creative_investment, budget_level,

growth_signals, storytelling_gap

status (New / Researched / Contacted / Active)

phase1_data (JSON), phase2_data (JSON)

outreach_email (text), notes, story_logic_version

youtube_data (JSON), created_at, updated_at

Other tables

• report_versions — archived phase2 snapshots for Compare modal

• niche_presets — custom sweep chips with targeting params

4. Scoring Formula

Prospect Score = (Creative Investment × 0.15) + (Budget Level × 0.25) + (Growth Signals × 0.30) + (Storytelling Gap × 0.30)

All four dimensions scored 1–10. Weights reflect strategic importance to a brand film pitch:

• Storytelling Gap (30%): How weak/generic is their video content? Higher = more opportunity for PMP.

• Growth Signals (30%): Scaling, fundraising, expanding? Growing brands spend more on content.

• Budget Level (25%): Can they afford $15K–$100K production? Revenue/funding signals.

• Creative Investment (15%): Are they already investing in video? Lower barrier to sale.

HOT PROSPECT threshold: 7.5+. Displayed in orange/red. Sorted highest-first in list and card views.

5. Deep Dive Data Pipeline (v2.2.4)

The deep dive runs as an async background thread. The pipeline is local-first: real data is collected before Claude is called, so Claude analyzes facts rather than guessing.

Step 1 — YouTube (local, free)

yt-dlp attempts to find the YouTube channel from the website URL or stored channel URL. If found, pulls top_viewed / recent / trending videos and fetches transcripts via youtube-transcript-api. No Claude call. If not found, sets channel_found: false and proceeds — use Re-pull Channel in the report UI to retry with a direct URL.

Step 2 — Meta Ad Library (local, free, no auth)

Calls the public Meta Ad Library search endpoint with the company name. Returns: active ad count, ad copy text samples with start dates, platforms, and funding entity. This is the source of Winner Signals — real ad longevity data, not Claude estimates.

Step 3 — Claude Call A: Company Intel (no web search)

Uses call_claude_no_search() — no web_search tool attached, so zero search result tokens against TPM limit. Claude answers from training knowledge. Returns: social handles, funding signals, SimilarWeb estimates, funnel architecture, team/agency intel, best contact, S01–S04, S08–S09, S10 sources, outreach email draft.

Rate limit context: Anthropic Tier 1 = 30K input tokens/minute. Web search tool burns search result tokens against this limit even on small prompts. All deep dive calls use no_search to stay well under.

Step 4 — Apify Social (optional, requires APIFY_API_KEY)

Uses confirmed Instagram/TikTok handles from Call A output. Fires fetch_apify_instagram() and fetch_apify_tiktok() — each pulls last 15 posts/videos with real follower counts, captions, engagement data. Gracefully skips if no key. Shows 'No Apify key' in report instead of estimated data.

• Instagram: apify/instagram-scraper actor — ~$0.002 per post

• TikTok: clockworks/tiktok-profile-scraper actor — ~$0.0017 per video

• Free tier: $5/month credit = ~70 deep dives before paying

Step 5 — Claude Call B: Story Analysis (no web search)

Uses call_claude_no_search(). Fed all local data via _fmt_social_context(). Returns S05 creative strategy, S06 storytelling diagnostic (People/Plot/Places/Purpose), S07 top 3 opportunities, and all prospect scores. story_logic.md injected here only, capped at 8,000 chars.

Merge

Call A intel + Call B story analysis + s_social from local data all merged into a single result dict and saved to phase2_data in the database.

6. Report Sections (S01–S10 + YT)

|   |   |   |
|---|---|---|
|Item|Status|Notes|
|S01 Company Overview|✓ Built|Metrics bar, description, key context block|
|S02 Ad Spend Estimation|✓ Built|Table + visual gauge bar ($0→$100K)|
|S03 Performance Metrics|✓ Built|Meta/Google ad counts, SimilarWeb traffic table|
|S04 Funnel Architecture|✓ Built|Funnel type, flow, key elements list|
|S05 Creative Strategy|✓ Built|Format breakdown, themes table, Winner Signals, S/W grid|
|S06 Storytelling Diagnostic|✓ Built|4 Pillars (People/Plot/Places/Purpose), composite score|
|S07 Top 3 Opportunities|✓ Built|Gap / What PMP Delivers / Predicted Impact cards|
|S08 Agency Intelligence|✓ Built|Status, Confirmed Partner block, team table, capability gap|
|S09 Revenue-as-a-Service|✓ Built|Baseline metrics, projected uplift callout, offer structure|
|S10 Data Sources|✓ Built|2-column link grid of sources used|
|YouTube Intelligence|✓ Built|Channel strip, transcript viewer, Re-pull modal|
|Social Strip|✓ Built|YouTube/Instagram/TikTok/Facebook/LinkedIn cells|

7. Key Claude Prompts

Phase 1 Sweep System Prompt

You are a brand film prospect researcher for Peter McCabe Pictures,

a premium brand film production company in Los Angeles.

Find real companies with real websites.

Return ONLY valid JSON, no markdown fences, no extra text.

Phase 1 Sweep User Prompt (core structure)

Search the web and find 12-15 REAL companies in the '{genre}' space

that are growing brands with a need for brand film / video production.

Score each on:

1. Creative Investment (1-10): Are they investing in video content right now?

2. Budget Level (1-10): Can they afford $15K-$100K production?

3. Growth Signals (1-10): Scaling, fundraising, expanding?

4. Storytelling Gap (1-10): How weak/generic is their video content?

Prospect Score = (Creative ×0.15) + (Budget ×0.25) + (Growth ×0.30) + (Gap ×0.30)

Return ONLY valid JSON. hot=true if score >= 7.5.

Call A System Prompt (Company Intel)

You are a brand intelligence researcher for Peter McCabe Pictures.

Use your training knowledge to answer.

Flag any field you are not confident about with confidence: Low.

Do not fabricate — if unknown, use null or 'Unknown'.

Return ONLY valid JSON, no markdown, no fences.

Call A User Prompt (key fields requested)

Research this company for a brand film prospect report.

Company: {company} / Website: {website} / Founder: {founder}

Find and return:

- Company overview (revenue, funding, distribution, awards, press)

- Exact Instagram handle (@handle or null)

- Exact TikTok handle (@handle or null)

- LinkedIn followers and post frequency

- SimilarWeb traffic (visits, sources, bounce rate)

- Meta Ad Library (ad count, platforms, spend estimate)

- Google Ads status and estimated spend

- Website tech stack (Shopify, Klaviyo, etc.)

- Funnel architecture

- Known marketing team or agency relationships

- Best contact for outreach (name, role, LinkedIn URL)

Returns: s01–s04, s08–s10, outreach_email, instagram_handle, tiktok_handle

Call B System Prompt (Story Analysis)

You are a brand film story analyst for Peter McCabe Pictures — Los Angeles.

35+ years experience. HBO Max, Netflix credits. Motion Picture Editors Guild.

Analyze ONLY the data provided — do not search the web.

Every score requires specific evidence from the data below.

Return ONLY valid JSON, no markdown, no fences.

Call B User Prompt (core structure)

Analyze creative strategy and storytelling gaps for: {company}

MUSE STORYTELLING FRAMEWORK:

{story_logic[:8000]}  ← capped at 8K chars

--- END FRAMEWORK ---

VERIFIED LOCAL DATA (do not search — use only what is below):

{social_context}  ← Meta ads, Instagram captions, TikTok captions, YT transcripts

Company context: tagline, overview, funnel type

CRITICAL: s07_opportunities MUST contain EXACTLY 3 items.

Returns: prospect_score, all 4 sub-scores, s05, s06, s07

Re-analyze Prompt (partial — S05/S06/S07 only)

Re-analyze creative strategy and storytelling for: {company}

Uses stored YouTube transcripts as context.

Merges result back into existing phase2_data.

Archives previous version to report_versions table.

ALSO re-runs s_social (social scores update on re-analyze).

8. Open Build Items

High Priority

• YouTube smart search + disambiguation: Search YouTube for company name via yt-dlp ytsearch, auto-select if one strong match, surface options modal if multiple, prompt for manual URL if none.

• Source links in story analysis: Call A saves sources_used[] field. S10 populated with real URLs. Inline cite markers in S01/S05/S06 where claims reference specific sources.

Medium Priority

• Email composer redesign: Inline email draft in S09 report section (collapsed/expandable). Tone controls. Send-ready output. Currently functional but unstyled.

• Apify key activation: Add APIFY_API_KEY to ~/.bash_profile to enable real Instagram/TikTok data on next deep dive.

Future Features

• Marp/pitch deck output from report data

• Apollo.io / Hunter.io contact enrichment for founder direct contact

• Soft delete for prospects (currently hard delete, no recovery)

• Story Logic re-analyze flag (banner exists, partial implementation)

• Confidence badges on S01 metrics (template built, only shows on new deep dives)

9. Deploy Workflow

10. Download build files into ~/Desktop/Projects/Lead_Research_Intel/pmp-intel/

11. Double-click deploy.command

  — Auto-unzips if needed

  — Copies files to templates/

  — Detects Anaconda Python automatically

  — Restarts Flask on port 5200

  — Opens Safari to localhost:5200

12. Done.

Never needs chmod — just drop new files or zip into pmp-intel/ and double-click deploy.command.

10. Session Handoff Protocol

Files to upload at start of every session

• app.py

• report.html

• index.html

• VERSION

• STORY_LOGIC_VERSION

• HANDOFF_vX_X_X.md (most recent)

Opening prompt template

Continuing Lead Research Intel development.

Flask app, port 5200, SQLite DB, pmp-intel/ folder.

Currently App v2.2.4 / SL v1.2.

All files uploaded.

Session goal: [describe what you want to tackle]

Version bump rules

• App VERSION — bump on every build (patch for fixes, minor for features, major for big changes)

• STORY_LOGIC_VERSION — bump ONLY when story_logic.md content actually changes

Browser workflow

When testing in browser: tell Claude the URL to navigate to and what to click. Claude watches via screenshot. You do the button pushing. This saves tokens and keeps you in the loop.

11. Rate Limits & API Tier

Current tier: Tier 1

• 30,000 input tokens per minute (ITPM)

• Web search tool use burns search result tokens against ITPM — even small prompts can hit 30K when Claude makes multiple searches

• Solution: all deep dive calls use call_claude_no_search() — no web_search tool attached

• If you hit 429: wait 60–90 seconds (token bucket refills continuously) then retry

To upgrade to Tier 2 (80K ITPM)

• Go to platform.anthropic.com/settings/limits

• Deposit $40 cumulative — advances to Tier 2 immediately

• Tier 2 provides 80K ITPM — enough headroom for the full pipeline with Apify

Peter McCabe Pictures  •  Lead Research Intel  •  Confidential

Built with Claude Sonnet 4  •  App v2.2.4  •  April 2026

Peter McCabe Pictures  •  Confidential  •  Page
