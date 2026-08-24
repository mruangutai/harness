#!/usr/bin/env python3
"""Render a ship-review briefing into a reading view — DERIVED, NEVER AUTHORED.

  render-brief.py <briefing.md> [...]      writes a sibling <briefing>.html each

The markdown briefing is the record the orchestrator writes and the main session
presents; this is a deterministic projection of it for the human who reads it once
to make a ship decision. Same law as render-map.py (DEC-141): **no agent writes
HTML, ever.** A hand-authored HTML copy of a briefing is the duplication-drift
class this repo has killed twice (DEC-126 templates, DEC-135 CLAUDE.md) — and it
would also cost a briefing-sized model spend per feature to produce something a
regex can produce for free.

Zero judgment, so it needs no owner and no freshness policy: it is exactly as
fresh as the markdown beside it. Re-running it IS the refresh.

WHY NOT SHARE render-map.py's converter: that one has no table support, and a
briefing is table-heavy — the proposed backlog and the verification evidence are
both tables, and piped rows rendered as paragraphs are unreadable. Extracting a
shared converter would fix the map's tables too and is worth doing; it is a
change to the map's output and so is NOT smuggled in here.

Stdlib only, no network, no CDN — a briefing has no diagrams to lazy-load, so
unlike map.html this file works identically offline.
"""
import html
import os
import re
import sys

# Blue-biased neutrals over warm cream: the subject is gates, exit codes and pinned
# SHAs, and monospace carries the identity because the content IS identifiers.
CSS = """
:root{
  --ink:#16202b; --paper:#fbfcfd; --sunk:#f1f4f7; --line:#dbe2e9;
  --slate:#5b6b7c; --quiet:#7d8b99; --accent:#2b5c8a; --accent-soft:#e8f0f7;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --sans:ui-sans-serif,-apple-system,"Segoe UI","Helvetica Neue",Arial,sans-serif;
}
/* Token-level theming: components style through the tokens and never inside the
   media query, so the viewer's explicit toggle can override the OS in BOTH
   directions. */
@media (prefers-color-scheme:dark){
  :root{ --ink:#e4eaf0; --paper:#11171e; --sunk:#182029; --line:#293441;
         --slate:#9aa9b8; --quiet:#77869a; --accent:#7fb2dd; --accent-soft:#1a2733; }
}
:root[data-theme="dark"]{
  --ink:#e4eaf0; --paper:#11171e; --sunk:#182029; --line:#293441;
  --slate:#9aa9b8; --quiet:#77869a; --accent:#7fb2dd; --accent-soft:#1a2733;
}
:root[data-theme="light"]{
  --ink:#16202b; --paper:#fbfcfd; --sunk:#f1f4f7; --line:#dbe2e9;
  --slate:#5b6b7c; --quiet:#7d8b99; --accent:#2b5c8a; --accent-soft:#e8f0f7;
}
*{box-sizing:border-box}
body{margin:0; background:var(--paper); color:var(--ink);
  font:400 16px/1.65 var(--sans); padding:clamp(1.5rem,5vw,4rem) clamp(1rem,5vw,2rem) 6rem}
.wrap{max-width:56rem; margin:0 auto}
/* Layout owns the spacing: gap between siblings, not per-element margins that
   collapse or double. */
.wrap{display:flex; flex-direction:column; gap:1rem}
.eyebrow{font:500 11px/1 var(--mono); letter-spacing:.14em; text-transform:uppercase;
  color:var(--quiet); margin:0}
h1{font:600 clamp(1.6rem,4vw,2.3rem)/1.15 var(--sans); letter-spacing:-.02em;
  margin:.4rem 0 .2rem; text-wrap:balance}
h2{font:600 1.15rem/1.3 var(--sans); letter-spacing:-.01em; margin:2rem 0 0;
  padding-top:1.25rem; border-top:1px solid var(--line); text-wrap:balance}
h3{font:600 .98rem/1.4 var(--sans); margin:1.1rem 0 0}
h4,h5,h6{font:500 11px/1.4 var(--mono); letter-spacing:.1em; text-transform:uppercase;
  color:var(--quiet); margin:1rem 0 0}
p,li{max-width:65ch; margin:0}
ul,ol{margin:0; padding-left:1.4rem; display:flex; flex-direction:column; gap:.4rem}
li>ul,li>ol{margin-top:.4rem}
strong{font-weight:600}
code{font:400 .875em/1.5 var(--mono); background:var(--sunk); padding:.1em .35em; border-radius:3px}
pre{background:var(--sunk); border:1px solid var(--line); border-radius:6px;
  padding:.85rem 1rem; overflow-x:auto; margin:0}
pre code{background:none; padding:0}
blockquote{margin:0; padding:.75rem 1rem; border-left:3px solid var(--accent);
  background:var(--accent-soft); border-radius:0 5px 5px 0}
blockquote p{max-width:none}
hr{border:0; border-top:1px solid var(--line); margin:.5rem 0}
/* Wide content pans inside its OWN container; the page body never scrolls sideways. */
.scroll{overflow-x:auto; border:1px solid var(--line); border-radius:6px}
table{border-collapse:collapse; width:100%; font-size:.9rem}
th,td{text-align:left; padding:.6rem .8rem; border-bottom:1px solid var(--line); vertical-align:top}
thead th{font:500 10px/1.3 var(--mono); letter-spacing:.11em; text-transform:uppercase;
  color:var(--quiet); background:var(--sunk); white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
/* Figures in a column line up. */
td,th{font-variant-numeric:tabular-nums}
.derived{color:var(--slate); font-size:.85rem; margin-top:2.5rem;
  padding-top:1rem; border-top:1px solid var(--line)}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
"""


def inline(s):
    s = html.escape(s)
    # Code first: its span is literal, so a ** or _ inside a backtick run must not
    # be eaten by the emphasis passes below.
    holes = []

    def stash(m):
        holes.append(f"<code>{m.group(1)}</code>")
        return f"\x00{len(holes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", stash, s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: holes[int(m.group(1))], s)


def is_row(l):
    return l.lstrip().startswith("|")


def is_rule(l):
    """The |---|:--:| separator that makes the line above it a header row."""
    return bool(re.match(r"^\s*\|[\s|:-]+\|\s*$", l)) and "-" in l


def cells(l):
    return [c.strip() for c in l.strip().strip("|").split("|")]


def md_to_html(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)   # authoring metadata, not body prose
    lines = md.splitlines()
    out, i = [], 0
    while i < len(lines):
        l = lines[i]

        fence = re.match(r"^\s*```(\w*)\s*$", l)
        if fence:
            block, i = [], i + 1
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                block.append(lines[i]); i += 1
            i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(block))}</code></pre>")
            continue

        # Tables — the reason this converter exists rather than reusing render-map's.
        if is_row(l) and i + 1 < len(lines) and is_rule(lines[i + 1]):
            head = cells(l)
            i += 2
            body = []
            while i < len(lines) and is_row(lines[i]):
                body.append(cells(lines[i])); i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            rows = []
            for r in body:
                # Pad/truncate to the header width: a ragged row otherwise shifts
                # every later cell one column left and silently mislabels data.
                r = (r + [""] * len(head))[:len(head)]
                rows.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append(f'<div class="scroll"><table><thead><tr>{th}</tr></thead>'
                       f"<tbody>{''.join(rows)}</tbody></table></div>")
            continue

        h = re.match(r"^(#{1,6})\s+(.*)$", l)
        if h:
            n = len(h.group(1))
            tag = "h1" if n == 1 else f"h{min(n, 6)}"
            out.append(f'<{tag} id="{slug(h.group(2))}">{inline(h.group(2))}</{tag}>')
            i += 1
            continue

        if re.match(r"^\s*(---|\*\*\*|___)\s*$", l):
            out.append("<hr>")
            i += 1
            continue

        bullet = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", l)
        if bullet:
            tag = "ul" if bullet.group(2) in "-*+" else "ol"
            items, base = [], len(bullet.group(1))
            while i < len(lines):
                m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", lines[i])
                if not m or len(m.group(1)) != base:
                    # A wrapped continuation line belongs to the item above it,
                    # not to a new paragraph after the list.
                    if items and lines[i].strip() and lines[i].startswith(" " * (base + 2)):
                        items[-1] += " " + lines[i].strip(); i += 1
                        continue
                    break
                items.append(m.group(3)); i += 1
            # inline() runs on the JOINED item, never per source line: a `**bold**`
            # that straddles a wrap boundary leaves an unpaired ** in each half and
            # renders as literal asterisks (observed on the first real briefing).
            out.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
            continue

        if l.lstrip().startswith(">"):
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(inline(lines[i].lstrip()[1:].strip())); i += 1
            out.append("<blockquote><p>" + " ".join(quote) + "</p></blockquote>")
            continue

        if l.strip():
            # A briefing is hard-wrapped at ~100 columns, so one <p> per SOURCE line
            # turns every paragraph into a stack of orphan lines. Consecutive prose
            # lines are one paragraph; a blank line or any block opener ends it.
            # The first line is consumed unconditionally: a line that IS a block
            # opener only reaches here when its block branch declined it (a `|` row
            # with no separator beneath), and re-testing it would never advance `i`.
            para = [l.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not starts_block(lines[i]):
                para.append(lines[i].strip()); i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
            continue
        i += 1
    return "\n".join(out)


def starts_block(l):
    """True when a line opens a non-paragraph block, so a paragraph must stop before it."""
    return bool(re.match(r"^\s*(#{1,6}\s|```|>|[-*+]\s|\d+[.)]\s|\|)", l)
                or re.match(r"^\s*(---|\*\*\*|___)\s*$", l))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"[`*]", "", s).lower()).strip("-")


def render(src):
    md = open(src, encoding="utf-8").read()
    m = re.search(r"^#\s+(.*)$", md, re.M)
    title = m.group(1).strip() if m else os.path.basename(src)[:-3]
    rel = os.path.basename(src)
    doc = ("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
           "<meta name='viewport' content='width=device-width,initial-scale=1'>"
           f"<title>{html.escape(re.sub(r'[`*]', '', title))}</title>"
           f"<style>{CSS}</style></head><body><div class='wrap'>"
           f"<p class='eyebrow'>Ship review · reading view</p>"
           f"{md_to_html(md)}"
           f"<p class='derived'>Derived from <code>{html.escape(rel)}</code> — the markdown is the "
           "record; do not edit this file. Regenerate with <code>bin/render-brief.py</code>.</p>"
           "</div></body></html>")
    out = src[:-3] + ".html" if src.endswith(".md") else src + ".html"
    open(out, "w", encoding="utf-8").write(doc)
    return out


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    rc = 0
    for src in argv:
        if not os.path.isfile(src):
            print(f"render-brief: no such file: {src}", file=sys.stderr)
            rc = 1
            continue
        print(f"render-brief: wrote {render(src)}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
