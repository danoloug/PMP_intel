
`Here's how pmp-db-manager should work, grounded in the schema we just built and the operating rules in CLAUDE.md.`
  1. `Its role: the single gateway`
  `It is the only skill that touches the DB. Every other skill (pmp-industry-sweep, pmp-company-analyzer, pmp-outreach-composer, etc.) calls it, never the`

  `SQLite MCP directly. So its SKILL.md should expose a small, named operation vocabulary — not "run this SQL." Callers say what they want; this skill owns
  `how.`

  `It is the only place mcp__pmp-sqlite__read_query / write_query / read_query are invoked.`

  2. `The operation set`

  `Design it around these verbs (each a section in SKILL.md with inputs → SQL → return shape):`

  `┌───────────────────────────────┬───────────────────────────────────────────────────────────┬───────────────────────────────┐`
  `│           Operation           │                       What it does                        │       Key rule enforced       │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ upsert_prospect               │ Insert or update one company by dedupe key                │ Idempotent — never duplicates │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ get_prospect / list_prospects │ Read one / filter by industry + crm_stage                 │ Read path for renderer        │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ append_raw_pull               │ Insert a raw_data_pulls row                               │ Append-only, never overwrite  │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ save_youtube_videos           │ Bulk insert youtube_videos for a run                      │ —                             │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ save_analysis                 │ Insert an analyses row (one per analyzer)                 │ Append-only                   │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ assemble_report               │ Insert reports + report_sections, flip is_current         │ Versioning                    │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ update_scores                 │ Write sub-scores and compute composite                    │ Composite is derived here     │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────
  `│ set_crm_stage                 │ Move a prospect between pipeline stages                   │ Explicit transitions only     │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ record_outreach               │ Insert/append an outreach draft; on "sent" advance stages │ Stage coupling                │`
  `├───────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────┤`
  `│ log_run                       │ Write a run_log row at every agent start/finish           │ Always, even on failure       │`
  `└───────────────────────────────┴───────────────────────────────────────────────────────────┴───────────────────────────────\]

  

  3. `The four rules it must mechanically enforce`

  Idempotency / dedupe. upsert_prospect needs a stable key. company_name alone is fragile (punctuation, "Inc."). Recommend: normalize website_url host (strip scheme/www/trailing slash) as the primary match, fall back to lowercased company_name + industry. On match → UPDATE existing row + bump` last_analyzed_at; on no match → INSERT. Re-analysis never creates a second prospects row, but always appends a new analyses/reports row.`

  Composite is derived, never passed in. Analyzers supply only the four sub-scores (creative_score, budget_score, growth_score, other_day_score, each 0–10). update_scores computes composite_score (0–100) and writes both atomically. You need to pick a weighting — here's a sane default to put in SKILL.md,`
  tunable later:`

  composite = round( 10 * ( creative*0.30 + budget*0.20 + growth*0.30 + other_day*0.20 ) )`
  
  Store the weighting version in scoring_logic_version so old scores stay interpretable when you retune.`

  CRM stage machine. set_crm_stage rejects illegal jumps. Allowed: lead → in_research → contacted → active, plus → archived from any stage, and explicit re-open archived → in_research. A sweep starting calls lead → in_research; record_outreach(status=sent) calls in_research → contacted; a logged reply calls contacted → active. No skipping (e.g. lead → contacted is an error the skill raises, not silently allows).`

  Report versioning. assemble_report runs as one logical unit: UPDATE reports SET is_current=0 WHERE prospect_id=? AND is_current=1, then insert the new report with is_current=1, then its report_sections. Old reports/sections are never deleted.`

  4. `run_id discipline`
 
 The orchestrator generates one run_id (UUID) at the start of a sweep/analysis and passes it down. pmp-db-manager stamps it on raw_data_pulls, analyses, reports, and run_log so a whole research run is reconstructable. SKILL.md should state: callers pass run_id; this skill never invents one.`

  4. `Failure behavior`

  

  `Per CLAUDE.md, fail loud, not silent. If the SQLite MCP is unavailable or a write fails: write a run_log row with status='failed' + error_message if it`

  `can, return a clear error to the caller, and do not return a partial success. Reads that find nothing return an explicit "not found," never a fabricated`

  `row.`

  5. `SKILL.md shape`

  `~/.claude/skills/pmp-db-manager/SKILL.md`
    `- Frontmatter: name, description ("Called by all other PMP skills;`
      `sole reader/writer of pmp_intel.db")`
    `- "When invoked" — operation dispatch table`
    `- One section per operation: inputs, the exact SQL, return JSON shape`
    `- Invariants block: the four rules above, verbatim`
    `- Composite formula + current scoring_logic_version`
    `- Schema reference: points to schema_md/DB_schema.md as source of truth`

  `Keep the SQL in the skill, expressed as concrete mcp__pmp-sqlite__* calls — that's the allowed exception to "markdown-first," because a DB gateway genuinely needs it.`