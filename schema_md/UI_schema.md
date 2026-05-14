# Story Gap Intel — UI Schema
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

---

## Screen 1: Dashboard (index)

The main landing screen. Shows all prospects as either cards or a list.

### Header bar
- Left: "Story Gap Studio" in small caps, muted cream
- Center: "BRAND FILM INTEL" in DM Mono, gold, larger
- Right: app version (e.g. v2.2.4) and story logic version (e.g. SL v1.2) in DM Mono, muted

### Controls row (below header)
- Left: search field — filters prospect cards in real time by company name
- Center: toggle between Card View and List View (two icon buttons)
- Right: "+ Add Prospect" button in gold

### Card View
Cards sorted best-to-worst, left-to-right, top-to-bottom.
Each card shows:
- Company name in Cormorant Garamond, large
- Overall prospect score as a large champagne numeral (0–100)
- Story Gap Score and Economic Viability Score as smaller sub-scores below
- Status badge (new / researched / contacted / responded) in muted color
- Outreach stage indicator
- Last researched date in DM Mono, small and muted
- "View Report" button
- Three-dot menu: Re-run Deep Dive, Archive, Delete (with scary confirmation warning)

If a prospect has new YouTube transcripts available but the report hasn't been regenerated
with them, show a green banner at the bottom of the card: "New transcripts available — Re-Analyze"

### List View
Same data as cards but in a compact table format.
Columns: Company | Score | Story Gap | Status | Outreach | Last Researched | Actions
Sortable by clicking column headers.
Each row has a "View Report" link and a three-dot actions menu.

### Add Prospect modal
Triggered by "+ Add Prospect" button.
Fields: Company Name (required), Website URL, Instagram Handle, YouTube Channel,
Industry, Revenue Estimate.
"Save and Research Now" button runs a deep dive immediately.
"Save Only" adds to dashboard without running research.

---

## Screen 2: Report Page (report)

The full intelligence report for a single prospect.
Premium editorial layout. Feels like a high-end strategy document.

### Report Header
Full-width dark panel with:
- Company name in Cormorant Garamond, very large, champagne
- Overall score as the dominant visual — huge champagne numeral, right side
- Below the score: Story Gap Score, Economic Viability Score, Muse sub-scores
  (People / Plot / Place / Purpose) as smaller labeled numerals
- App version and Story Logic version in DM Mono, bottom right, muted
- Report generated date
- If new YouTube transcripts exist but haven't been incorporated:
  green banner across the bottom of the header: "New transcripts available — Re-Analyze with Transcripts"
- Buttons: "Print / Export PDF", "Re-Run Deep Dive", "Draft Outreach Email"

### YouTube Panel
Appears between the header and section 1.
Shows all videos pulled for this prospect.

Each video row shows:
- Thumbnail
- Title
- View count
- Transcript status icon (none / pulled / summarized / failed)
- Expandable transcript preview — click to reveal first 200 words

Preset selector: SCOUT (5 videos) / STANDARD (10) / DEEP (18)
"Pull More Videos" button runs yt-dlp for additional discovery.
Live progress display during pulls: shows current video title + view count + transcript status
as each one completes.

If transcript pull fails: show a toast notification on dashboard + open a manual URL
field on the report page so user can paste a YouTube URL manually.

### Report Sections (1–10)

Each section has:
- Section number in DM Mono, small, gold, left-aligned
- Section title in Cormorant Garamond, medium, cream
- Gold rule line under the title
- Content below

Section order and layout:

**Section 01 — Company Overview**
Narrative paragraphs. Who they are, founding story, market position.
No tables.

**Section 02 — Ad Spend Intelligence**
Meta ad activity. Structured summary + a small data table if ad data is available.
Columns: Creative Theme | Estimated Spend Signal | Targeting Notes

**Section 03 — Market Performance**
Revenue range estimate, growth signals, traction indicators.
Key metrics as callout boxes — large number, small label below.

**Section 04 — Customer Acquisition Funnel**
How they find and convert customers. Narrative with a simple funnel diagram if applicable.

**Section 05 — Creative Identity**
Visual identity, brand voice, content style. Narrative paragraphs.
If YouTube transcripts are incorporated, this section references specific video evidence.

**Section 06 — Current Storytelling Analysis**
How they tell their story now. What's working, what's missing.
Muse Framework lens: People / Plot / Place / Purpose — each assessed in a labeled block.

**Section 07 — Story Gap Opportunities**
The most visually elevated section. Three opportunities, each in a full-width card.
Each card has:
- Gold top border, 3px
- Opportunity title in Cormorant Garamond, large
- "The Gap" column: what's missing in their current story
- "What Story Gap Studio Delivers" column: how a brand film closes that gap
- Impact callout box: bold statement about expected outcome
Cards stack vertically with generous spacing between them.

**Section 08 — Fit Assessment**
Two-column table comparing the brand's current state vs. what Story Gap Studio brings.
Current state column: muted terracotta tint
Story Gap Studio column: champagne gold tint
Makes the contrast immediately visible.

**Section 09 — Engagement Structure**
Suggested project framing, scope, and investment range.
Narrative with a simple two-row summary table at the end.

**Section 10 — Sources**
All URLs and data sources used. DM Mono font throughout.
Compact list, muted styling — not visually prominent.

### Version History drawer
Accessible via a "Previous Versions" link in the report header.
Slides in from the right as a panel.
Lists all prior reports for this prospect with dates and version numbers.
Click any version to view it (read-only).

---

## Screen 3: Email Composer

Accessed via "Draft Outreach Email" button on the report page.
Opens as a full-width modal overlay (not a separate page).

### Left panel — Email draft
- Subject line field (editable)
- Email body (editable rich text)
- Current tone badge showing active tone setting

### Right panel — Controls
- Tone selector: four buttons — Warm / Direct / Provocative / Formal
  Clicking a tone regenerates the email with that tone via Claude API call
- Free-text instruction field: "Make it shorter", "Add a specific reference to their founder story", etc.
  Submit button regenerates the email following the instruction
- "Regenerate from scratch" button — full new draft, same tone
- Version history: small list of previous drafts, click to restore

### Footer
- "Copy to Clipboard" button — copies subject + body as plain text
- "Mark as Sent" button — updates outreach status in database, records sent_at timestamp
- "Close" button — dismisses modal, no save needed (drafts are auto-saved)

---

## Shared Components

### Toast notifications
Small pill-shaped notifications that appear top-center and auto-dismiss after 4 seconds.
Gold border on success, terracotta border on error.
Examples: "Deep dive complete", "Transcript pull failed — manual URL field now open"

### Confirmation dialogs
Used only for destructive actions (delete prospect, re-run deep dive which overwrites data).
Dark modal with explicit warning text. Two buttons: Cancel (muted) and Confirm (gold).
Delete confirmation text: "Permanently delete this prospect? This cannot be undone —
all report data, notes, and research will be lost forever."

### Loading states
During any Claude API call or scraping run: show a pulsing champagne dot animation.
Long-running operations (deep dive, YouTube pull) show a live progress log —
each step appended as it completes, like a terminal feed but styled on-brand.

---

## Navigation

No persistent nav bar. Navigation is contextual:
- Dashboard → Report: click "View Report" on any card or list row
- Report → Dashboard: "← Back to Dashboard" link, top left of report header
- Report → Email Composer: "Draft Outreach Email" button opens modal
- Report → Version History: "Previous Versions" link opens right drawer

---

## Responsive Behavior

Optimized for desktop / large laptop screen (1200px+).
Report page minimum width: 960px — not designed for mobile.
Dashboard card grid collapses from 4 columns → 3 → 2 at narrower widths.
