#!/usr/bin/env python3
"""Tests for render-brief.py's markdown conversion.

WHY: the renderer is the ONLY path from a briefing to the artifact a human reads,
so a converter bug silently misrepresents a ship decision rather than failing. The
first real briefing exposed three of them at once, and each has a case below:

  - hard-wrapped prose became one <p> per SOURCE line (a briefing wraps at ~100 cols)
  - a `**bold**` straddling a wrap boundary left unpaired ** in each half
  - a ragged table row shifted every later cell one column left, MISLABELLING data

Assertions are on rendered structure, not on byte-equality with a golden file — a
golden file would make every CSS tweak a test failure.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import importlib.util
import os
import re
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
spec = importlib.util.spec_from_file_location("render_brief",
                                              os.path.join(HERE, "render-brief.py"))
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

CASES = []


def case(name, md, want_in=(), want_not_in=()):
    CASES.append((name, md, want_in, want_not_in))


# ---------------- paragraphs: wrapping is not structure ----------------
case("hard-wrapped prose is ONE paragraph",
     "All 12 criteria are met, verified at\n363b539 against the signed brief.",
     want_in=["<p>All 12 criteria are met, verified at 363b539 against the signed brief.</p>"])
case("a blank line still separates paragraphs",
     "First para.\n\nSecond para.",
     want_in=["<p>First para.</p>", "<p>Second para.</p>"])
case("bold straddling a wrap boundary still renders",
     "the toll once so that **every future\nfeature does not.**",
     want_in=["<strong>every future feature does not.</strong>"],
     want_not_in=["**"])

# ---------------- tables: the reason this converter exists ----------------
case("a table becomes a table, in its own scroll container",
     "| Line | Amount |\n|---|---|\n| validate | $49 |",
     want_in=["<table>", "<th>Line</th>", "<td>validate</td>", "class=\"scroll\""],
     want_not_in=["<p>|"])
case("a RAGGED row is padded, never shifted left",
     "| a | b | c |\n|---|---|---|\n| 1 | 2 |",
     want_in=["<td>1</td><td>2</td><td></td>"])
case("an over-long row is truncated to the header width",
     "| a | b |\n|---|---|\n| 1 | 2 | 3 |",
     want_in=["<td>1</td><td>2</td></tr>"],
     want_not_in=["<td>3</td>"])
case("a pipe line with NO separator row is prose, not a table",
     "the operator | is literal here",
     want_in=["<p>"], want_not_in=["<table>"])

# ---------------- inline: code is literal ----------------
case("asterisks inside backticks are not emphasis",
     "run `sed -i '' 's/*/x/'` now",
     want_in=["<code>"], want_not_in=["<em>"])
case("a bare underscore in an identifier is not emphasis",
     "the `cycles_used` field and max_total_cycles",
     want_not_in=["<em>"])

# ---------------- lists ----------------
case("a wrapped list item stays one item",
     "- The validate phase was ~$49\n  across three runs.",
     want_in=["<li>The validate phase was ~$49 across three runs.</li>"])
case("a numbered list is an ol",
     "1. first\n2. second", want_in=["<ol>", "<li>first</li>"])

# ---------------- structure ----------------
case("an HTML comment is authoring metadata, not body prose",
     "<!-- ok-stale -->\nreal prose", want_not_in=["ok-stale"])
case("a fenced block is escaped, not interpreted",
     "```\n<script>x</script>\n```", want_in=["&lt;script&gt;"], want_not_in=["<script>x"])
case("headings keep their level and get an anchor",
     "## The conclusion", want_in=['<h2 id="the-conclusion">The conclusion</h2>'])


def main():
    fails = 0
    for name, md, want_in, want_not_in in CASES:
        try:
            got = rb.md_to_html(md)
        except Exception as e:                     # a hang or crash is a failure, not a skip
            print(f"FAIL  {name}\n        raised {type(e).__name__}: {e}")
            fails += 1
            continue
        bad = [f"missing {s!r}" for s in want_in if s not in got]
        bad += [f"unexpected {s!r}" for s in want_not_in if s in got]
        if bad:
            fails += 1
            print(f"FAIL  {name}")
            for b in bad:
                print(f"        {b}")
            print(f"      got: {got[:200]}")
        else:
            print(f"ok    {name}")

    # Every non-void tag the converter can emit must close. Counted rather than
    # eyeballed, because an unclosed <div> swallows the rest of the briefing.
    doc = rb.md_to_html("# T\n\npara\n\n| a |\n|---|\n| 1 |\n\n- x\n\n> q\n\n```\nc\n```")
    for tag in ("div", "table", "tbody", "thead", "tr", "td", "th", "ul", "li",
                "p", "blockquote", "pre", "code"):
        o = len(re.findall(rf"<{tag}[ >]", doc))
        c = doc.count(f"</{tag}>")
        if o != c:
            print(f"FAIL  tag balance: <{tag}> opened {o}, closed {c}")
            fails += 1
    if not fails:
        print("ok    every emitted tag is balanced")

    print(f"\n{len(CASES) + 1 - fails}/{len(CASES) + 1} checks passed.")
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
