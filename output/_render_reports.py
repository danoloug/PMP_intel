#!/usr/bin/env python3
"""
PMP Intel — bulk renderer for Company Sweep Review HTML.
Reads pmp_intel.db, renders one self-contained HTML report per prospect
with a current report, writes into the same output/ directory.

Idempotent: overwrites existing files. Run after any sweep or re-analysis.
Path-independent: uses absolute project paths.
"""
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path("/Users/dano/Projects/Claude_CLI/PMP_Intel")
DB = ROOT / "pmp_intel.db"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)


def slug(name: str) -> str:
    s = name.lower()
    # Strip diacritics simply (é→e, etc.) — keep ASCII fallback
    s = (s.replace("é", "e").replace("è", "e").replace("ë", "e")
           .replace("á", "a").replace("í", "i").replace("ó", "o").replace("ú", "u")
           .replace("&", "and"))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def esc(x) -> str:
    if x is None:
        return "—"
    s = str(x)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


CSS = """
/* Theme v2 — readability pass: alphas bumped (0.30→0.62, 0.45→0.80, 0.75→0.94)
   and font sizes increased (body 14→15.5, section text 12.5→14.5).
   Brand identity intact: Obsidian (#141414) + Champagne (#d4a840) preserved. */
:root{--bg:#141414;--panel:#1e1e1e;--panel-2:#242424;--gold:#d4a840;--score:#e8b347;
--cream:#f5f0e8;--cream-75:rgba(245,240,232,.94);--cream-45:rgba(245,240,232,.80);
--cream-30:rgba(245,240,232,.62);--border:rgba(255,255,255,.14);
--border-soft:rgba(255,255,255,.09);--green:#7ec49a;--blue:#7da3c8;--terracotta:#e07c6c;
--serif:"Cormorant Garamond",Georgia,serif;--sans:"DM Sans",-apple-system,sans-serif;
--mono:"DM Mono","SF Mono",ui-monospace,monospace;--rule:1px solid var(--border);--pad:28px;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--cream-75);font-family:var(--sans);font-size:15.5px;line-height:1.65;-webkit-font-smoothing:antialiased}
.app-header{display:flex;align-items:center;justify-content:space-between;padding:18px var(--pad);border-bottom:var(--rule)}
.app-header .brand{font-variant:small-caps;letter-spacing:.12em;color:var(--cream-45);font-size:14px}
.app-header .product{font-family:var(--mono);color:var(--gold);letter-spacing:.34em;font-size:16px}
.app-header .versions{font-family:var(--mono);color:var(--cream-30);font-size:13px;letter-spacing:.08em}
.btn-outline{font-family:var(--mono);font-size:12px;letter-spacing:.16em;color:var(--cream-45);
background:transparent;border:var(--rule);padding:9px 18px;cursor:pointer;text-decoration:none}
.btn-outline:hover{color:var(--gold);border-color:var(--gold)}
.kpi-strip{display:flex;align-items:center;border-bottom:var(--rule)}
.kpi{display:flex;align-items:baseline;gap:10px;padding:16px var(--pad);border-right:var(--rule)}
.kpi .num{font-size:28px;color:var(--cream);font-weight:500}
.kpi .lbl{font-family:var(--mono);font-size:12px;letter-spacing:.18em;color:var(--cream-45)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.dot.gold{background:var(--gold)}.dot.green{background:var(--green)}
.dot.blue{background:var(--blue)}.dot.red{background:var(--terracotta)}
.shell{display:flex;min-height:calc(100vh - 120px)}
.sidebar{width:320px;flex:0 0 320px;border-right:var(--rule);padding:22px var(--pad);overflow-y:auto}
.main{flex:1;padding:32px var(--pad);min-width:640px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.2em;color:var(--cream-45);margin-bottom:12px;display:block;text-decoration:none}
.eyebrow:hover{color:var(--gold)}
.mini{border-left:2px solid transparent;padding:14px 0 14px 14px;border-bottom:var(--border-soft);display:block;text-decoration:none}
.mini.active{border-left-color:var(--gold)}
.mini:hover{background:rgba(255,255,255,.03)}
.mini-top{display:flex;justify-content:space-between;align-items:baseline}
.mini-name{font-family:var(--serif);font-size:20px;color:var(--cream)}
.mini-score{font-family:var(--serif);font-size:20px;color:var(--score)}
.mini-meta{font-family:var(--mono);font-size:11px;letter-spacing:.12em;color:var(--cream-30);margin:5px 0 6px}
.mini-note{font-size:13.5px;color:var(--cream-45);line-height:1.5}
.co-name{font-family:var(--serif);font-size:44px;color:var(--cream);line-height:1.1}
.co-sub{font-family:var(--mono);font-size:13px;letter-spacing:.1em;color:var(--cream-45);margin:8px 0 20px}
.co-score{display:flex;align-items:baseline;gap:18px}
.co-score .big{font-family:var(--serif);font-size:68px;color:var(--score);line-height:1}
.co-score .verdict{font-family:var(--mono);font-size:13px;letter-spacing:.2em;color:var(--gold)}
.subscores{display:flex;gap:42px;margin:20px 0 22px}
.subscore .v{font-family:var(--serif);font-size:30px;color:var(--cream)}
.subscore .k{font-family:var(--mono);font-size:11px;letter-spacing:.16em;color:var(--cream-45)}
.headline{font-family:var(--serif);font-size:20px;color:var(--cream-75);font-style:italic;margin-bottom:20px;max-width:820px;line-height:1.5}
.actions{display:flex;gap:10px;margin-bottom:28px;flex-wrap:wrap}
.tag{font-family:var(--mono);font-size:12px;letter-spacing:.12em;border:var(--rule);padding:8px 16px;color:var(--cream-45)}
.tag.stage{color:var(--green);border-color:rgba(126,196,154,.5)}
.section{border-top:var(--rule)}
.section>summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;padding:22px 4px}
.section>summary::-webkit-details-marker{display:none}
.section .s-title{font-family:var(--serif);font-size:28px;color:var(--cream)}
.section .s-num{font-family:var(--mono);font-size:13px;color:var(--gold);letter-spacing:.16em;margin-right:16px}
.section .chev{color:var(--cream-45);font-family:var(--mono);font-size:16px}
.section[open] .chev{color:var(--gold)}
.section-body{padding:4px 4px 32px}
.kv{margin:8px 0;font-size:14.5px;color:var(--cream-75);line-height:1.6}
.kv b{color:var(--cream);font-weight:600}
.metrics{display:flex;gap:48px;flex-wrap:wrap;padding:20px 0 24px}
.metric .v{font-family:var(--serif);font-size:26px;color:var(--cream);line-height:1.2}
.metric .k{font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--cream-45);margin-top:6px}
.highlight-box{border-left:3px solid var(--gold);background:rgba(212,168,64,.08);padding:16px 18px;font-size:14.5px;color:var(--cream-75);margin-top:18px;line-height:1.6}
.highlight-box .lead{color:var(--gold);font-family:var(--mono);font-size:12px;letter-spacing:.14em;display:block;margin-bottom:8px}
ul.clean{list-style:none;margin:10px 0;padding-left:6px}
ul.clean li{font-size:14.5px;color:var(--cream-75);line-height:1.7;padding-left:14px;position:relative}
ul.clean li::before{content:"·";color:var(--gold);position:absolute;left:0;top:-3px;font-size:20px;line-height:1}
.mix-strip{display:flex;border:var(--rule);margin:8px 0 26px;background:rgba(255,255,255,.02)}
.mix{flex:1;text-align:center;padding:26px 10px;border-right:var(--rule)}
.mix:last-child{border-right:0}
.mix .pct{font-family:var(--serif);font-size:36px;color:var(--cream)}
.mix .lbl{font-family:var(--mono);font-size:11px;letter-spacing:.18em;color:var(--cream-45);margin-top:6px}
table.theme{width:100%;border-collapse:collapse;margin-bottom:26px}
table.theme th{text-align:left;font-family:var(--mono);font-size:11px;letter-spacing:.16em;color:var(--cream-45);font-weight:500;padding:12px 14px;border-bottom:var(--rule)}
table.theme td{padding:16px 14px;vertical-align:top;border-bottom:var(--border-soft);font-size:14.5px;color:var(--cream-75);line-height:1.55}
table.theme td.theme-name{color:var(--cream);width:220px;font-weight:500}
table.theme td.share{color:var(--score);font-family:var(--serif);font-size:18px;width:80px}
.signals{border:1px solid rgba(212,168,64,.5);background:rgba(212,168,64,.08);padding:18px 22px;margin-bottom:26px}
.signals .cap{font-family:var(--mono);font-size:11px;letter-spacing:.16em;color:var(--gold);margin-bottom:14px}
.signals ul{list-style:none}
.signals li{font-size:14.5px;line-height:1.7;color:var(--cream-75);padding-left:18px;position:relative;margin-bottom:4px}
.signals li::before{content:"▸";color:var(--gold);position:absolute;left:0}
.swot{display:flex;gap:42px}
.swot .col{flex:1}
.swot .cap{font-family:var(--mono);font-size:11px;letter-spacing:.16em;margin-bottom:14px}
.swot .strengths .cap{color:var(--green)}
.swot .gaps .cap{color:var(--terracotta)}
.swot ul{list-style:none}
.swot li{font-size:14.5px;line-height:1.7;color:var(--cream-75);padding-left:18px;position:relative;margin-bottom:6px}
.swot .strengths li::before{content:"▸";color:var(--green);position:absolute;left:0}
.swot .gaps li::before{content:"▸";color:var(--terracotta);position:absolute;left:0}
.opp{border-top:3px solid var(--gold);background:var(--panel);padding:22px 24px;margin-bottom:18px}
.opp h4{font-family:var(--serif);font-size:23px;color:var(--cream);margin-bottom:10px}
.opp .col2{display:flex;gap:32px;margin:10px 0}
.opp .col2 div{flex:1;font-size:14.5px;color:var(--cream-75);line-height:1.6}
.opp .lab{font-family:var(--mono);font-size:10px;letter-spacing:.16em;color:var(--cream-45);display:block;margin-bottom:6px}
.opp .impact{color:var(--gold);font-size:14px;margin-top:12px;line-height:1.5}
.src{font-family:var(--mono);font-size:13px;color:var(--cream-45);line-height:2}
.src a{color:var(--cream-75);text-decoration:none;display:block}
.src a:hover{color:var(--gold)}
footer.legal{text-align:center;font-family:var(--mono);font-size:11px;color:var(--cream-45);padding:24px;border-top:var(--rule);letter-spacing:.1em}
"""


def render_kv_block(d: dict) -> str:
    """Render a dict as <p class='kv'><b>key</b> value</p>"""
    out = []
    for k, v in d.items():
        if isinstance(v, dict) and "value" in v:
            src = v.get("source", "")
            src_html = f' <span style="color:var(--cream-30)">— {esc(src)}</span>' if src else ""
            out.append(f'<p class="kv"><b>{esc(k.replace("_"," ").title())}:</b> {esc(v["value"])}{src_html}</p>')
        elif isinstance(v, list):
            out.append(f'<p class="kv"><b>{esc(k.replace("_"," ").title())}:</b></p><ul class="clean">' +
                       "".join(f"<li>{esc(x)}</li>" for x in v) + "</ul>")
        elif isinstance(v, dict):
            inner = "".join(f'<p class="kv"><b>{esc(kk.replace("_"," ").title())}:</b> {esc(vv)}</p>'
                            for kk, vv in v.items())
            out.append(f'<p class="kv"><b>{esc(k.replace("_"," ").title())}:</b></p>{inner}')
        else:
            out.append(f'<p class="kv"><b>{esc(k.replace("_"," ").title())}:</b> {esc(v)}</p>')
    return "\n".join(out)


def render_section_body(key: str, payload) -> str:
    """Dispatch by section_key to produce a styled body. payload may be dict or list."""
    if key == "company_overview":
        d = payload if isinstance(payload, dict) else {}
        metrics = d.get("metric_tiles") or d.get("metrics") or {}
        narr = d.get("narrative") or d.get("summary") or ""
        pos = d.get("position") or ""
        tiles_html = ""
        if metrics:
            tiles = []
            for k, v in metrics.items():
                tiles.append(f'<div class="metric"><div class="v">{esc(v)}</div>'
                             f'<div class="k">{esc(k.replace("_"," ").upper())}</div></div>')
            tiles_html = f'<div class="metrics">{"".join(tiles)}</div>'
        pos_html = (f'<div class="highlight-box"><span class="lead">MARKET POSITION</span>{esc(pos)}</div>'
                    if pos else "")
        return f'{tiles_html}<p style="color:var(--cream-45);font-size:13px">{esc(narr)}</p>{pos_html}'

    if key == "ad_spend_estimation":
        d = payload if isinstance(payload, dict) else {}
        out = []
        if "signal_band" in d or "spend_band" in d:
            out.append(f'<p class="kv"><b>Signal band:</b> {esc(d.get("signal_band") or d.get("spend_band"))}</p>')
        if "narrative" in d:
            out.append(f'<p class="kv">{esc(d["narrative"])}</p>')
        if "reasoning" in d:
            out.append(f'<p class="kv">{esc(d["reasoning"])}</p>')
        if d.get("channels"):
            out.append('<ul class="clean">' +
                       "".join(f"<li>{esc(c)}</li>" for c in d["channels"]) + "</ul>")
        if "limitation" in d or "data_source_limit" in d:
            lim = d.get("limitation") or d.get("data_source_limit")
            out.append(f'<div class="highlight-box"><span class="lead">DATA LIMITATION</span>{esc(lim)}</div>')
        return "\n".join(out)

    if key == "performance_metrics":
        return render_kv_block(payload if isinstance(payload, dict) else {})

    if key == "funnel_architecture":
        d = payload if isinstance(payload, dict) else {}
        out = []
        for k in ("model", "acquisition", "conversion_path", "detail", "friction"):
            if k in d:
                v = d[k]
                if isinstance(v, list):
                    out.append(f'<p class="kv"><b>{esc(k.replace("_"," ").title())}:</b></p>'
                               '<ul class="clean">' +
                               "".join(f"<li>{esc(x)}</li>" for x in v) + "</ul>")
                else:
                    out.append(f'<p class="kv"><b>{esc(k.replace("_"," ").title())}:</b> {esc(v)}</p>')
        if d.get("channels"):
            out.append('<p class="kv"><b>Channels:</b></p><ul class="clean">' +
                       "".join(f"<li>{esc(c)}</li>" for c in d["channels"]) + "</ul>")
        return "\n".join(out)

    if key == "creative_strategy":
        d = payload if isinstance(payload, dict) else {}
        mix = d.get("mix", {})
        out = []
        if mix:
            cells = []
            for label in ("video", "static", "carousel", "ab_testing"):
                if label in mix:
                    cells.append(f'<div class="mix"><div class="pct">{esc(mix[label])}%</div>'
                                 f'<div class="lbl">{label.upper().replace("_"," ")}</div></div>')
            out.append(f'<div class="mix-strip">{"".join(cells)}</div>')
        themes = d.get("themes", [])
        if themes:
            rows = []
            for t in themes:
                rows.append(f'<tr><td class="theme-name">{esc(t.get("name"))}</td>'
                            f'<td class="share">{esc(t.get("share"))}</td>'
                            f'<td>{esc(t.get("description"))}</td></tr>')
            out.append('<table class="theme"><thead><tr><th>THEME</th><th>SHARE</th><th>DESCRIPTION</th></tr></thead>'
                       f'<tbody>{"".join(rows)}</tbody></table>')
        ws = d.get("winner_signals", [])
        if ws:
            out.append('<div class="signals"><div class="cap">▸ WINNER SIGNALS</div><ul>' +
                       "".join(f"<li>{esc(x)}</li>" for x in ws) + "</ul></div>")
        strengths = d.get("strengths", [])
        gaps = d.get("gaps", [])
        if strengths or gaps:
            s_html = ("".join(f"<li>{esc(x)}</li>" for x in strengths))
            g_html = ("".join(f"<li>{esc(x)}</li>" for x in gaps))
            out.append(f'<div class="swot"><div class="col strengths"><div class="cap">▸ STRENGTHS</div>'
                       f'<ul>{s_html}</ul></div>'
                       f'<div class="col gaps"><div class="cap">▸ WEAKNESSES / GAPS</div>'
                       f'<ul>{g_html}</ul></div></div>')
        if d.get("score_rationale") or d.get("creative_score") is not None:
            out.append(f'<p style="color:var(--cream-30);font-family:var(--mono);font-size:10px;margin-top:14px">'
                       f'creative_score {esc(d.get("creative_score"))} · {esc(d.get("score_rationale",""))}</p>')
        return "\n".join(out)

    if key == "storytelling_diagnostic":
        d = payload if isinstance(payload, dict) else {}
        out = []
        cur = d.get("current_state") or d.get("current") or ""
        if cur:
            out.append(f'<p class="kv"><b>Current state:</b> {esc(cur)}</p>')
        wk = d.get("whats_working") or d.get("working") or []
        ms = d.get("whats_missing") or d.get("missing") or []
        if wk or ms:
            out.append('<div class="swot">'
                       '<div class="col strengths"><div class="cap">▸ WORKING</div><ul>' +
                       "".join(f"<li>{esc(x)}</li>" for x in wk) +
                       '</ul></div><div class="col gaps"><div class="cap">▸ MISSING</div><ul>' +
                       "".join(f"<li>{esc(x)}</li>" for x in ms) +
                       '</ul></div></div>')
        return "\n".join(out)

    if key == "opportunities":
        items = payload.get("items") if isinstance(payload, dict) else payload
        items = items or []
        out = []
        for o in items:
            out.append(
                f'<div class="opp"><h4>{esc(o.get("title"))}</h4>'
                f'<div class="col2"><div><span class="lab">THE GAP</span>{esc(o.get("the_gap"))}</div>'
                f'<div><span class="lab">WHAT WE DELIVER</span>{esc(o.get("what_we_deliver"))}</div></div>'
                f'<div class="impact">Impact — {esc(o.get("impact"))}</div></div>'
            )
        return "\n".join(out)

    if key == "fit_assessment":
        d = payload if isinstance(payload, dict) else {}
        cur = d.get("current_state", [])
        bring = d.get("what_we_bring", [])
        return ('<div class="swot">'
                '<div class="col gaps"><div class="cap">▸ CURRENT STATE</div><ul>' +
                "".join(f"<li>{esc(x)}</li>" for x in cur) +
                '</ul></div><div class="col strengths"><div class="cap">▸ WHAT WE BRING</div><ul>' +
                "".join(f"<li>{esc(x)}</li>" for x in bring) +
                '</ul></div></div>')

    if key == "engagement":
        d = payload if isinstance(payload, dict) else {}
        out = []
        for k in ("suggested_structure", "structure", "investment_framing", "why_now", "note"):
            if k in d:
                out.append(f'<p class="kv"><b>{esc(k.replace("_"," ").title())}:</b> {esc(d[k])}</p>')
        return "\n".join(out)

    if key == "sources":
        items = payload.get("items") if isinstance(payload, dict) else payload
        items = items or []
        links = []
        for s in items:
            if isinstance(s, dict) and "url" in s:
                links.append(f'<a href="{esc(s["url"])}">{esc(s.get("title", s["url"]))}</a>')
            elif isinstance(s, dict) and "accessed_at" in s:
                links.append(f'<span style="color:var(--cream-30)">accessed {esc(s["accessed_at"])}</span>')
        return '<div class="src">' + "".join(links) + "</div>"

    # Fallback — show JSON
    return f'<pre style="color:var(--cream-45);font-size:11px;font-family:var(--mono);white-space:pre-wrap">{esc(json.dumps(payload, indent=2))}</pre>'


SECTION_TITLES = {
    "company_overview": "Company Overview",
    "ad_spend_estimation": "Ad Spend Estimation",
    "performance_metrics": "Performance Metrics",
    "funnel_architecture": "Funnel Architecture",
    "creative_strategy": "Creative Strategy Analysis",
    "storytelling_diagnostic": "Storytelling Diagnostic",
    "opportunities": "Opportunities",
    "fit_assessment": "Fit Assessment",
    "engagement": "Engagement Structure",
    "sources": "Sources",
}


def build_sidebar(prospects: list, active_id: int) -> str:
    """Sidebar mini-cards listing all prospects, active one marked."""
    out = ['<a href="industry_sweep_acoustic-guitar-manufacturers.html" '
           'class="eyebrow" style="display:block;margin-bottom:18px">&larr; BACK TO SWEEP</a>']
    for p in prospects:
        is_active = (p["id"] == active_id)
        cls = "mini active" if is_active else "mini"
        href = "" if is_active else f' href="company_{slug(p["company_name"])}.html"'
        tag = "a" if href else "div"
        out.append(
            f'<{tag} class="{cls}"{href}>'
            f'<div class="mini-top"><span class="mini-name">{esc(p["company_name"])}</span>'
            f'<span class="mini-score">{esc(p["composite_score"])}</span></div>'
            f'<div class="mini-meta">{esc(p["crm_stage"]).upper()} · ACOUSTIC GUITAR MANUFACTURERS</div>'
            f'</{tag}>'
        )
    return "\n".join(out)


def build_report_html(prospect: dict, sections: list, all_prospects: list, kpi_counts: dict) -> str:
    rj = json.loads(prospect["report_json"])
    verdict = rj.get("verdict", "")
    headline = rj.get("headline", "")
    host = (prospect.get("website_url") or "").replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")

    # KPI strip
    k = kpi_counts
    kpi_html = (
        f'<div class="kpi-strip">'
        f'<div class="kpi"><span class="num">{k["total"]}</span><span class="lbl"><span class="dot gold"></span> TOTAL PROSPECTS</span></div>'
        f'<div class="kpi"><span class="num">{k["in_research"]}</span><span class="lbl"><span class="dot green"></span> IN RESEARCH</span></div>'
        f'<div class="kpi"><span class="num">{k["contacted"]}</span><span class="lbl"><span class="dot blue"></span> CONTACTED</span></div>'
        f'<div class="kpi"><span class="num">{k["active"]}</span><span class="lbl"><span class="dot red"></span> ACTIVE</span></div>'
        f'</div>'
    )

    # Sub-scores
    sub_html = (
        f'<div class="subscores">'
        f'<div class="subscore"><div class="v">{esc(prospect["creative_score"])}</div><div class="k">CREATIVE</div></div>'
        f'<div class="subscore"><div class="v">{esc(prospect["budget_score"])}</div><div class="k">BUDGET</div></div>'
        f'<div class="subscore"><div class="v">{esc(prospect["growth_score"])}</div><div class="k">GROWTH</div></div>'
        f'<div class="subscore"><div class="v">{esc(prospect["other_day_score"])}</div>'
        f'<div class="k" title="⚠ definition unconfirmed — pending user decision">OTHER DAY ⚠</div></div>'
        f'</div>'
    )

    # Sections — Section 01 open, others collapsed
    sec_html = []
    for s in sections:
        n = s["section_number"]
        key = s["section_key"]
        title = SECTION_TITLES.get(key, key.replace("_", " ").title())
        try:
            payload = json.loads(s["content_json"])
        except Exception:
            payload = {}
        body = render_section_body(key, payload)
        opn = " open" if n == 1 else ""
        chev = "▾" if n == 1 else "▸"
        sec_html.append(
            f'<details class="section"{opn}>'
            f'<summary><span class="s-title"><span class="s-num">{n:02d}</span>{title}</span>'
            f'<span class="chev">{chev}</span></summary>'
            f'<div class="section-body">{body}</div></details>'
        )

    return f"""<!DOCTYPE html>
<!-- PMP Intel · Company Sweep Review · rendered by output/_render_reports.py from pmp_intel.db (report {prospect['report_id']}) -->
<html lang="en"><head><meta charset="utf-8"><title>PMP Intel — {esc(prospect['company_name'])}</title>
<style>{CSS}</style></head><body>

<div class="app-header">
  <span class="brand">PMP Intel</span>
  <span class="product">PMP&nbsp;INTEL</span>
  <span class="versions">v2.2.4 &nbsp;·&nbsp; pmp-score-v1</span>
  <a class="btn-outline" href="industry_sweep_acoustic-guitar-manufacturers.html">&larr; SWEEP</a>
</div>

{kpi_html}

<div class="shell">
  <aside class="sidebar">{build_sidebar(all_prospects, prospect['id'])}</aside>
  <main class="main">
    <div class="co-name">{esc(prospect['company_name'])}</div>
    <div class="co-sub">ACOUSTIC GUITAR MANUFACTURERS · {esc(host)}</div>
    <div class="co-score">
      <span class="big">{esc(prospect['composite_score'])}<span style="font-size:24px;color:var(--cream-30)">/100</span></span>
      <span class="verdict">{esc(verdict)}</span>
    </div>
    {sub_html}
    {('<div class="headline">' + esc(headline) + '</div>') if headline else ''}
    <div class="actions">
      <span class="tag stage">{esc(prospect['crm_stage']).upper().replace('_',' ')}</span>
      <span class="tag">RE-ANALYZE</span>
      <span class="tag">DRAFT OUTREACH</span>
      <span class="tag">ARCHIVE</span>
    </div>
    {"".join(sec_html)}
  </main>
</div>

<footer class="legal">PMP INTEL · COMPANY SWEEP REVIEW · {esc(prospect['company_name'].upper())} · REPORT {prospect['report_id']} · pmp-score-v1</footer>
</body></html>
"""


def main():
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    prospects = [dict(r) for r in conn.execute("""
        SELECT p.id, p.company_name, p.website_url, p.composite_score,
               p.creative_score, p.budget_score, p.growth_score, p.other_day_score,
               p.crm_stage, r.id AS report_id, r.report_json
        FROM prospects p JOIN reports r ON r.prospect_id = p.id
        WHERE r.is_current = 1 AND p.industry = 'acoustic guitar manufacturers'
        ORDER BY p.composite_score DESC NULLS LAST, p.id
    """).fetchall()]

    if not prospects:
        print("No current reports found.")
        return

    counts_rows = conn.execute("""
        SELECT crm_stage, COUNT(*) AS n FROM prospects
        WHERE industry='acoustic guitar manufacturers'
        GROUP BY crm_stage
    """).fetchall()
    cmap = {r["crm_stage"]: r["n"] for r in counts_rows}
    kpi = {
        "total": sum(cmap.values()),
        "in_research": cmap.get("in_research", 0),
        "contacted": cmap.get("contacted", 0),
        "active": cmap.get("active", 0),
    }

    written = []
    for p in prospects:
        sections = [dict(r) for r in conn.execute(
            "SELECT section_number, section_key, content_json "
            "FROM report_sections WHERE prospect_id=? ORDER BY section_number",
            (p["id"],)
        ).fetchall()]
        html = build_report_html(p, sections, prospects, kpi)
        path = OUT / f"company_{slug(p['company_name'])}.html"
        path.write_text(html, encoding="utf-8")
        written.append(path.name)

    conn.close()
    print(f"Wrote {len(written)} reports to {OUT}/:")
    for n in written:
        print(f"  {n}")


if __name__ == "__main__":
    main()
