
""" text 
 How it's designed

  - Tightly scoped subroutine — owns exactly one section (creative_strategy) and one sub-score (creative_score). Explicitly forbidden from touching
  budget/growth/other_day, composite, the report, or CRM stage — the caller owns those.
  - Output shape pinned to the template contract — mix / themes / winner_signals / strengths / gaps exactly matches
  templates/creative_strategy_analysis.html, so the renderer can consume it without adaptation.
  - Honest degradation, no fabrication — no yt-dlp/transcript/Playwright MCP is configured, so transcripts are best-effort with truthful transcript_status;
  thin asset samples return creative_score: null + a warning rather than a guessed number. Fail-loud only on missing Brave.
  - Inverted scoring rubric made explicit: weak current creative + strong untapped story material = high score (big opportunity to close), which is the
  marketing-services value lens — consistent with the Taylor Guitars fixture (creative 4.5 despite a strong brand).
  - Append-only and idempotent via pmp-db-manager; shares the parent run_id.

  State of the build

  ┌───────────────────────┬──────────────────────────────────────────────────┐                                                           
  │         Skill         │                      Status                      │
  ├───────────────────────┼──────────────────────────────────────────────────┤
  │ pmp-db-manager        │ built + end-to-end tested                        │
  ├───────────────────────┼──────────────────────────────────────────────────┤
  │ pmp-company-analyzer  │ built                                            │
  ├───────────────────────┼──────────────────────────────────────────────────┤
  │ pmp-creative-analyzer │ built                                            │
  ├───────────────────────┼──────────────────────────────────────────────────┤
  │ pmp-industry-sweep    │ not yet — fans out company-analyzer subagents    │
  ├───────────────────────┼──────────────────────────────────────────────────┤
  │ pmp-html-renderer     │ not yet — templates exist, no skill to fill them │
  ├───────────────────────┼──────────────────────────────────────────────────┤
  │ pmp-outreach-composer │ not yet                                          │
  ├───────────────────────┼──────────────────────────────────────────────────┤
  │ pmp-orchestrator      │ not yet — top-level entry point                  │
  └───────────────────────┴──────────────────────────────────────────────────┘'
  
  The analyzer chain is now testable end-to-end against a single company on the clean DB ("Analyze Taylor Guitars"). The next structural piece is either
  pmp-html-renderer (to see results visually — templates are already built and waiting) or pmp-industry-sweep (to fan out the analyzer across a niche). Want
   me to run a live single-company test of the analyzer chain now, or build the next skill?
"""