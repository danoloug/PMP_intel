
`Here's a two-stage test — first isolate whether the API key itself works (independent of MCP), then confirm the MCP server is wired up.`

  

  `Stage 1 — Test the API key directly (run in your new terminal)`

  

  `This bypasses Claude Code entirely, so it tells you definitively whether the key is valid:`


  curl -s --get "https://api.search.brave.com/res/v1/web/search" --data-urlencode "q=Taylor Guitars marketing" --data-urlencode "count=3" -H "Accept: application/json" -H "X-Subscription-Token: $BRAVE_API_KEY" | head -c 400; echo

  

  `Valid key: you'll see JSON starting with {"query":{"original":"Taylor Guitars marketing"... and result data.`

  `Bad/missing key: {"type":"ErrorResponse",...} with a 401/422 message — fix the key before bothering with MCP.`

  

  `Tip: you can run this from inside Claude Code by typing !  followed by the command, so the output lands right in the session.`

  

  `Stage 2 — Test the MCP server (in the restarted Claude Code session)`

  `After /mcp shows brave-search connected, paste this prompt:`

  

  `▎ Use the brave-search MCP server to run a web search for "acoustic guitar manufacturers" and show me the top 3 result titles and URLs. Confirm which tool you called.`

  `If it returns live results via a mcp__brave-search__* tool (not the built-in WebSearch), the full chain — key → env → .mcp.json → MCP server — is working  `and Brave Search is ready for the PMP Intel sweeps.`

  `If Stage 1 passes but Stage 2 fails, the problem is env propagation (Claude Code still launched without BRAVE_API_KEY); if both fail, it's the key/plan`
  `(e.g. subscription not activated yet on the Brave dashboard).`