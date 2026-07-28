#!/usr/bin/env python3
"""Render .harness/codebase/*.md into one human-facing map.html — DERIVED, NEVER AUTHORED.

  render-map.py [project-root]     writes .harness/codebase/map.html

The markdown map is the single source of truth that agents author and consume
(DEC-137); this script is a deterministic projection of it for humans. No agent
writes HTML, ever — parallel authored copies are the duplication-drift class this
repo killed twice (DEC-126 templates, DEC-135 CLAUDE.md). Regenerated mechanically
at the end of the map mission and every ship-refresh; running it by hand IS the
manual refresh. Zero judgment, so it needs no owner and no freshness policy of its
own — it is exactly as fresh as the markdown.

Diagrams: authored as ```mermaid blocks in architecture.md (text, diffable,
anchorable). map.html loads mermaid.js from a CDN when a browser opens it; offline
it degrades to the diagram source in a code block. The files-only constraint
governs the harness runtime, not the viewer's browser.

Stdlib only. The md->html conversion is deliberately minimal (headings, fences,
lists, paragraphs, inline code) — the map is structured notes, not a book.
"""
import html
import os
import re
import sys

ORDER = ["INDEX.md", "architecture.md", "product-surface.md", "api-surface.md",
         "data-flows.md", "ui-surface.md", "llm-patterns.md", "trust-boundaries.md",
         "stack.md"]


def md_to_html(md):
    out, i, lines = [], 0, md.splitlines()
    in_list = False
    while i < len(lines):
        l = lines[i]
        fence = re.match(r"^```(\w*)\s*$", l)
        if fence:
            lang, block = fence.group(1), []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i]); i += 1
            i += 1
            body = "\n".join(block)
            if lang == "mermaid":
                # mermaid.js replaces <pre class="mermaid"> in-browser; without JS
                # (offline) the source itself stays visible — the graceful fallback.
                out.append(f'<pre class="mermaid">{html.escape(body)}</pre>')
            else:
                out.append(f"<pre><code>{html.escape(body)}</code></pre>")
            continue
        if in_list and not l.lstrip().startswith("- "):
            out.append("</ul>"); in_list = False
        h = re.match(r"^(#{1,4})\s+(.*)$", l)
        if h:
            n = min(len(h.group(1)) + 1, 5)   # page h1 is the title; content shifts down
            txt = inline(h.group(2))
            out.append(f'<h{n} id="{slug(h.group(2))}">{txt}</h{n}>')
        elif l.lstrip().startswith("- "):
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(l.lstrip()[2:])}</li>")
        elif l.strip():
            out.append(f"<p>{inline(l)}</p>")
        i += 1
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def collect(cb):
    """(section-id, title, markdown) in a stable order; domains/ nested last."""
    docs = []
    for name in ORDER:
        p = os.path.join(cb, name)
        if os.path.isfile(p):
            docs.append((slug(name[:-3]), name[:-3], open(p, encoding="utf-8").read()))
    ddir = os.path.join(cb, "domains")
    if os.path.isdir(ddir):
        for f in sorted(os.listdir(ddir)):
            if f.endswith(".md"):
                docs.append((slug("domain-" + f[:-3]), f"domains / {f[:-3]}",
                             open(os.path.join(ddir, f), encoding="utf-8").read()))
    return docs


CSS = """
:root { --bg:#fff; --fg:#1a1a1a; --side:#f6f6f4; --accent:#4a5d7e; --line:#e2e2de; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#16181d; --fg:#d8d8d4; --side:#1d2026; --accent:#8aa4cc; --line:#2a2e36; } }
* { box-sizing:border-box } body { margin:0; display:flex; background:var(--bg); color:var(--fg);
  font:15px/1.55 -apple-system,'Segoe UI',sans-serif }
nav { width:250px; min-width:250px; height:100vh; position:sticky; top:0; overflow-y:auto;
  background:var(--side); border-right:1px solid var(--line); padding:14px }
nav h1 { font-size:14px; text-transform:uppercase; letter-spacing:.08em; color:var(--accent) }
nav details { margin:2px 0 } nav summary { cursor:pointer; font-weight:600; padding:3px 0 }
nav a { display:block; color:var(--fg); text-decoration:none; padding:2px 0 2px 14px;
  font-size:13.5px; opacity:.85 } nav a:hover { color:var(--accent) }
main { flex:1; max-width:60rem; padding:24px 40px }
h2 { border-bottom:1px solid var(--line); padding-bottom:6px; margin-top:2.2em }
code { background:var(--side); padding:1px 5px; border-radius:4px; font-size:.92em }
pre { background:var(--side); padding:12px; border-radius:8px; overflow-x:auto }
pre.mermaid { background:transparent; text-align:center }
.meta { color:var(--accent); font-size:12.5px }
"""

JS = """
const s=document.createElement('script');
s.src='https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js';
s.onload=()=>mermaid.initialize({startOnLoad:true,theme:matchMedia('(prefers-color-scheme: dark)').matches?'dark':'default'});
s.onerror=()=>{}; /* offline: mermaid sources stay visible as text — the fallback IS the degradation */
document.head.appendChild(s);
"""


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    cb = os.path.join(root, ".harness", "codebase")
    if not os.path.isdir(cb):
        print("render-map: no .harness/codebase/ — nothing to render (run the map mission first)")
        return 0
    docs = collect(cb)
    if not docs:
        print("render-map: codebase/ has no views yet")
        return 0

    nav, body = [], []
    for sid, title, md in docs:
        heads = re.findall(r"^##\s+(.*)$", md, re.M)
        nav.append(f'<details open><summary><a href="#{sid}">{html.escape(title)}</a></summary>'
                   + "".join(f'<a href="#{sid}-{slug(h)}">{html.escape(h)}</a>' for h in heads)
                   + "</details>")
        # prefix section heading ids so same-named headings across views stay unique
        rendered = md_to_html(md)
        rendered = re.sub(r'id="([^"]+)"', lambda m: f'id="{sid}-{m.group(1)}"', rendered)
        body.append(f'<section id="{sid}"><h2>{html.escape(title)}</h2>{rendered}</section>')

    doc = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
           "<meta name='viewport' content='width=device-width,initial-scale=1'>"
           f"<title>Codebase map</title><style>{CSS}</style></head><body>"
           f"<nav><h1>Codebase map</h1>{''.join(nav)}"
           "<p class='meta'>Derived from .harness/codebase/*.md — do not edit; regenerate with "
           "bin/render-map.py. The map is a hint; code is truth.</p></nav>"
           f"<main>{''.join(body)}</main><script>{JS}</script></body></html>")
    out = os.path.join(cb, "map.html")
    open(out, "w", encoding="utf-8").write(doc)
    print(f"render-map: wrote {os.path.relpath(out, root)} ({len(docs)} view(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
