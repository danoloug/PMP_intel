
""" text
How it's designed

  - Single-company, single-run pipeline: open run → research (Brave + WebFetch, evidence captured via append_raw_pull) → delegate creative → synthesize 10
  sections → score → persist.
  - Strict boundaries enforced in the spec, matching the project rules:
    - No direct SQL — everything through pmp-db-manager operations.
    - Emits only the four sub-scores; composite_score is read back, never computed here (preserves the pmp-score-v1 derivation in pmp-db-manager).
    - No fabrication — unknown metrics become "insufficient evidence"; ad spend is a qualitative band, not an invented dollar figure (since no
  Playwright/Meta Ad Library MCP is configured).
    - Fail-loud on missing Brave MCP, with a log_run failure row.
    - 
  - Section contract maps 1:1 to the report_sections.section_key enum and the Company Sweep Review screenshot; creative_strategy is delegated verbatim to
  pmp-creative-analyzer.
  
  - Scoring rubrics with 0–10 anchors for budget and growth. other_day_score carries the documented ⚠️  unconfirmed-definition flag (consistent with the
  project memory), with a working definition and a warnings entry in the return payload so the caller surfaces it.
  
  - Idempotent / re-run safe and CRM-forward-only, leaning on pmp-db-manager's dedupe and report versioning.

  Dependency note

  This skill delegates to pmp-creative-analyzer, which doesn't exist yet — the spec handles its absence gracefully (continues with 9 sections,
  creative_score = NULL, records the gap), but a real run won't produce a creative section until that skill is built.

  Logical next step: build pmp-creative-analyzer (YouTube discovery + transcripts → creative-mix/theme/signals + creative_score), then both can be tested
  together end-to-end against Taylor Guitars on the now-clean DB. Want me to scaffold it?
"""