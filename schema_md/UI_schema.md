# PMP Intel — UI Schema
# Natural language description for Claude Code CLI
# Describes every screen, component, and interaction in plain English

---

## Design Language

The app feels like a premium intelligence tool — cinematic, editorial, serious.
It does not look like a startup dashboard or a SaaS product.

Color palette: Obsidian and Champagne.
- Background: near-black (#141414)
- Cards and panels: dark charcoal (#1e1e1e to #2a2a2a)
- Accent: champagne gold (#d4a840)
- Body text: warm cream (#f5f0e8 at 75% opacity)
- Borders: white at 7–11% opacity
- Success signals: muted green (#60a880)
- Alert signals: muted terracotta (#d06050)

Typography:
- Display / section headers: Cormorant Garamond (serif, elegant)
- Body and UI labels: DM Sans (clean sans-serif)
- Data / version numbers / codes: DM Mono (monospace)

Spacing is generous. Nothing feels cramped.
Gold rule lines separate major sections.

There are three canonical views: **Industry Sweep**, **Company Sweep Review**,
and **Creative Strategy Analysis**. Reference screenshots maintained by the
user in the project directory are the visual source of truth — read them
before rendering or editing templates.

---

## View 1: Industry Sweep (dashboard / index)

The main landing screen for an industry. A grid of scored company cards with
a CRM pipeline rail down the left side.

### Header bar
- Left: the marketing services business name in small caps, muted cream
- Center: "PMP INTEL" in DM Mono, gold, larger
- Right: app version (e.g. v2.2.4) and scoring logic version (e.g. SL v1.2)
  in DM Mono, muted

### CRM pipeline rail (left side)
A vertical pipeline with four stages, matching `prospects.crm_stage`:
`Lead → In-Research → Contacted → Active`. Each stage shows a count of
prospects in it. Clicking a stage filters the card grid to that stage.
`Archived` prospects are hidden by default; a small "Show archived" toggle
at the bottom of the rail reveals them.

### Controls row (below header)
- Left: search field — filters cards in real time by company name
- Center: toggle between Card View and List View (two icon buttons)
- Right: "+ Add Prospect" button in gold, and an "Export CSV" button
  (exports the current filtered prospect set)

### Card View
Cards sorted best-to-worst by composite score, left-to-right, top-to-bottom.
The grid is 4 columns, collapsing to 3 → 2 at narrower widths.
Each card shows:
- Company name in Cormorant Garamond, large
- Composite score as a large champagne numeral (0–100)
- The four sub-scores below, small and labeled:
  Creative / Budget / Growth / Other Day (each 0–10)
- CRM stage badge (lead / in_research / contacted / active) in muted color
- Outreach stage indicator (none / drafted / sent / replied / closed)
- Last analyzed date in DM Mono, small and muted
- "View Report" button
- Three-dot menu: Re-Analyze, Move to <next stage>, Archive,
  Delete (with scary confirmation warning)

If a prospect has new YouTube transcripts available but its report has not
been regenerated with them, show a green banner at the bottom of the card:
"New transcripts available — Re-Analyze"

### List View
Same data as cards in a compact table.
Columns: Company | Composite | Creative | Budget | Growth | Other Day |
CRM Stage | Outreach | Last Analyzed | Actions
Sortable by clicking column headers.
Each row has a "View Report" link and a three-dot actions menu.

### Add Prospect modal
Triggered by "+ Add Prospect".
Fields: Company Name (required), Website URL, Instagram Handle,
YouTube Channel, Industry, Revenue Estimate.
"Save and Analyze Now" runs a sweep/analysis immediately (moves the
prospect Lead → In-Research). "Save Only" adds it as a Lead without
running analysis.

---

## View 2: Company Sweep Review (report page)

The full intelligence report for a single prospect.
Premium editorial layout. Feels like a high-end strategy document.

### Report Header
Full-width dark panel with:
- "← Back to Sweep" link, top left
- Company name in Cormorant Garamond, very large, champagne
- Composite score as the dominant visual — huge champagne numeral, right side
- Below the score: the four sub-scores
  (Creative / Budget / Growth / Other Day) as smaller labeled numerals
- App version and scoring logic version in DM Mono, bottom right, muted
- Report generated date
- If new YouTube transcripts exist but haven't been incorporated:
  green banner across the bottom of the header:
  "New transcripts available — Re-Analyze with Transcripts"
- Buttons: "Print / Export PDF", "Re-Analyze", "Draft Outreach"

### YouTube Panel
Appears between the header and section 1. Shows all videos pulled for this
prospect (feeds the Creative Strategy Analysis).

Each video row shows:
- Thumbnail
- Title
- View count
- Transcript status icon (none / pulled / summarized / failed)
- Expandable transcript preview — click to reveal first 200 words

Preset selector: SCOUT (5 videos) / STANDARD (10) / DEEP (18)
"Pull More Videos" button runs yt-dlp for additional discovery.
Live progress display during pulls: current video title + view count +
transcript status as each one completes.

If transcript pull fails: show a toast on the sweep view + open a manual URL
field on the report page so the user can paste a YouTube URL manually.

### Report Sections (expandable, 1–10)

Each section has:
- Section number in DM Mono, small, gold, left-aligned
- Section title in Cormorant Garamond, medium, cream
- Gold rule line under the title
- Content below; sections are individually expandable/collapsible

Section order maps to `report_sections.section_key`:

**Section 01 — Company Overview** (`company_overview`)
Narrative paragraphs. Who they are, founding story, market position. No tables.

**Section 02 — Ad Spend Estimation** (`ad_spend_estimation`)
Meta ad activity. Structured summary + a small data table if available.
Columns: Creative Theme | Estimated Spend Signal | Targeting Notes

**Section 03 — Performance Metrics** (`performance_metrics`)
Revenue range estimate, growth signals, traction indicators.
Key metrics as callout boxes — large number, small label below.

**Section 04 — Funnel Architecture** (`funnel_architecture`)
How they acquire and convert customers. Narrative with a simple funnel
diagram if applicable.

**Section 05 — Creative Strategy Analysis** (`creative_strategy`)
The Creative Strategy Analysis view, embedded. See View 3 for full layout.

**Section 06 — Storytelling Diagnostic** (`storytelling_diagnostic`)
How they tell their story now: what's working, what's missing.
Strengths and gaps in labeled blocks.

**Section 07 — Opportunities** (`opportunities`)
The most visually elevated section. Three opportunities, each in a
full-width card with a gold 3px top border:
- Opportunity title in Cormorant Garamond, large
- "The Gap" column: what's missing in their current marketing
- "What We Deliver" column: how the marketing service closes that gap
- Impact callout box: bold statement about expected outcome
Cards stack vertically with generous spacing.

**Section 08 — Fit Assessment** (`fit_assessment`)
Two-column table comparing the brand's current state vs. what this
marketing services business brings.
Current state column: muted terracotta tint.
Our offering column: champagne gold tint.

**Section 09 — Engagement Structure** (`engagement`)
Suggested project framing, scope, and investment range.
Narrative with a simple two-row summary table at the end.

**Section 10 — Sources** (`sources`)
All URLs and data sources used. DM Mono throughout.
Compact list, muted styling — not visually prominent.

### Version History drawer
Accessible via a "Previous Versions" link in the report header.
Slides in from the right. Lists all prior reports for this prospect with
dates and version numbers (one row per `reports` record, newest first;
the `is_current` report is marked). Click any version to view it read-only.

---

## View 3: Creative Strategy Analysis

The creative deep-dive. Appears both as Section 05 of the Company Sweep
Review and as a standalone view ("Show me the creative analysis for [company]").

### Creative Mix panel
Four percentages shown as a horizontal stacked bar plus labeled numerals:
Video / Static / Carousel / A/B. Percentages sum to 100.

### Theme Share table
Columns: Theme | Share % | Example Asset | Notes
One row per recurring creative theme detected.

### Winner Signals
A list of high-performing creative patterns, each as a small card with a
muted-green left border and a one-line evidence note.

### Strengths / Weaknesses
Two side-by-side columns:
- Strengths: muted-green accent, bulleted
- Weaknesses & Gaps: muted-terracotta accent, bulleted
The contrast is immediately visible.

---

## View 4: Outreach Composer

Accessed via "Draft Outreach" on the report page.
Opens as a full-width modal overlay (not a separate page).

### Left panel — Draft
- Channel toggle: Email / LinkedIn (maps to `outreach.channel`)
- Subject line field (editable; hidden when channel = LinkedIn)
- Message body (editable rich text)
- Current tone badge showing the active tone

### Right panel — Controls
- Tone selector: four buttons — Warm / Direct / Provocative / Formal.
  Clicking a tone regenerates the message with that tone via Claude API.
- Free-text instruction field ("Make it shorter", "Reference their founder
  story", etc.). Submit regenerates following the instruction.
- "Regenerate from scratch" button — full new draft, same tone
- Version history: list of previous drafts (one per `outreach` row),
  click to restore

### Footer
- "Copy to Clipboard" — copies subject + body as plain text
- "Mark as Sent" — sets `outreach.status = sent`, records `sent_at`, and
  advances the prospect `outreach_stage` to `sent` (and CRM stage
  In-Research → Contacted if not already past it)
- "Close" — dismisses modal; drafts are auto-saved

---

## Shared Components

### Toast notifications
Small pill-shaped notifications, top-center, auto-dismiss after 4 seconds.
Gold border on success, terracotta border on error.
Examples: "Sweep complete", "Transcript pull failed — manual URL field now open"

### Confirmation dialogs
Used only for destructive actions (delete prospect, re-analyze which
overwrites the current report). Dark modal with explicit warning text.
Two buttons: Cancel (muted) and Confirm (gold).
Delete confirmation text: "Permanently delete this prospect? This cannot be
undone — all report data, notes, and research will be lost forever."
Note: deletion is discouraged; archiving (crm_stage = archived) is preferred.

### Loading states
During any Claude API call or scraping run: a pulsing champagne dot animation.
Long-running operations (sweep, YouTube pull) show a live progress log —
each step appended as it completes, like a terminal feed but on-brand.

---

## Navigation

No persistent nav bar. Navigation is contextual:
- Industry Sweep → Company Sweep Review: click "View Report" on a card/row
- Company Sweep Review → Industry Sweep: "← Back to Sweep" link, top left
- Company Sweep Review → Outreach Composer: "Draft Outreach" opens modal
- Company Sweep Review → Version History: "Previous Versions" opens right drawer
- Creative Strategy Analysis is reachable inline (Section 05) or standalone

---

## Responsive Behavior

Optimized for desktop / large laptop screen (1200px+).
Report page minimum width: 960px — not designed for mobile.
Industry Sweep card grid collapses from 4 columns → 3 → 2 at narrower widths.
