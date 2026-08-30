# UI Reviewer — panel c2 — citation-sweep delta (`2557950`..`48bbe7e`)

## BLUF
No application UI in this delta — confirmed by extension census, not assumed. One artifact in the
delta genuinely renders (`notes/ship-review-2026-08-29-16.html`) and it has two real defects: a
broken/empty code example that hides the document's own headline evidence, and a WCAG AA contrast
failure (light theme only) on both data tables' column headers. The 18 citation-edit hunks across
13 files read as clean, natural prose — no defect found there.

## 1. No-UI census (measured, not predicted)
`git -C <wt> diff 2557950 48bbe7e --stat` — 26 files, +1041/-77. File-extension breakdown: 24 are
`.md`/`.yaml`/`.json`/`.snippet`; **one** `.html`. Zero `.css`/`.scss`/`.tsx`/`.jsx`/`.vue`/`.svelte`/`.less`,
zero application components or templates. Confirms the dispatch's own framing: no application UI
surface exists in this delta.

## 2. `notes/ship-review-2026-08-29-16.html` — the one file that renders
Opened via `git show 48bbe7e:<path>` (raw bytes, bypasses any tool-side rendering). It is a
self-contained styled HTML document (`lang='en'`, `<title>` present, token-based CSS, both
`prefers-color-scheme` media query and a `data-theme` override for explicit toggle, `:focus-visible`,
`prefers-reduced-motion` respected). Structurally it renders coherently — headings, two data tables,
blockquote-free prose, tag nesting balanced.

**Finding A — severity `med` — broken code example, verified against source.**
`notes/ship-review-2026-08-29-16.html:78` is `<pre><code></code></pre>` — empty. The source markdown
at `notes/ship-review-2026-08-29-16.md:51-53` has one fenced line:
`<!-- claim: git -c "alias.zz=!touch /tmp/p_f" zz :: nothing -->` — the concrete payload for the
document's headline claim (the reachable RCE hole). It is the only fenced code block in the whole
document, and it is the one that's gone. Read live, the sentence is: "A claim marker in a markdown
file reading [nothing] executed its payload." — the one piece of evidence for the most safety-critical
claim in the ship review is invisible to the reader deciding whether to ship.
Root-caused (read-only, not executed): `.claude/skills/harness/bin/render-brief.py:143` in the
**current** tree (untouched by this delta) does call `html.escape()` on fenced-block content before
emitting it — a fresh render of this exact markdown would not reproduce an empty block. So the
committed `.html` is either stale or was not produced by the script its own footer credits
("Regenerate with `bin/render-brief.py`"). Not gating on its own — the underlying security substance
was independently verified by the security reviewer per the document's own text — but it is a real
content-fidelity defect in a committed, reader-facing artifact.

**Finding B — severity `high` — WCAG AA contrast failure, light theme, both tables' headers.**
`--quiet` is `#7d8b99` on `--paper` `#fbfcfd` in light mode (`ship-review-2026-08-29-16.html:5-8`
token block; consumed by `thead th` at line ~54 and `.eyebrow` at line ~43). Computed via the
standard WCAG relative-luminance formula: **≈3.39:1**, against the AA floor of **4.5:1** for
normal-size text (this text is 10–11px, nowhere near the 18px/24px large-text exemption). This token
colors the column headers of **both** data tables in the document — "Criterion"/"Result" on the SC
table, "ID"/"Nature"/"Finding" on the backlog table — plus the `.eyebrow` strap line. A low-vision
reader in light mode cannot reliably read what a column means.
The asymmetry is the tell: the dark-mode equivalent (`--quiet:#77869a` on `--paper:#11171e`, line 13)
computes to **≈4.86:1** and passes — dark mode was tuned to clear AA, light mode was not. No other
pairing in the sheet fails: `.derived`/`--slate` on light paper ≈5.34:1, link `--accent` on light
paper ≈6.83:1 — both pass. There is no DESIGN.md for this feature, so the "specified" side of this
finding is the general WCAG 2.1 AA floor, not a written contract.

**Not applicable, stated explicitly rather than omitted:** interaction/focus/keyboard-reachability —
the document has zero `<a>` and zero other interactive elements (`grep -c "<a "` = 0), so
`:focus-visible` is defined but exercises nothing. No state is conveyed by colour alone (table
results are bold text — "met"/"not_met"/"unrun — yours" — not colour-coded).

## 3. Reader-facing prose quality of the 18 T-14 citation edits
Opened the full diff for all 13 named files (`git diff 2557950 48bbe7e -- <13 paths>`) — 18 hunks,
one line changed each except `harness/SKILL.md` (4) and `github-mirror.md` (2). Read every resulting
sentence in context. All read as grammatically complete natural prose: no doubled spaces, no orphaned
punctuation, no dangling parenthetical fragments, no "citation removed mid-sentence" artifact.
Two edits are notable enough to verify rather than skim:
- `.claude/skills/harness/SKILL.md` "(am.2)" → "(DEC-145)": confirmed by reading `DEC-145`'s body —
  it literally states "A lead skims the run's digests and offers each member at most 3 sourced…"
  which is exactly the sentence it now cites. Correct successor, not a guess.
- `.claude/skills/harness/references/debug-mission.md:23` — `"approval bypasses grow (DEC-19)."` →
  `"approval bypasses grow."` — reads as intended prose. The pattern was already stated in words
  *before* the citation ("a second, lighter lane is how approval bypasses grow"), so dropping only
  the parenthetical (per T-14's own instruction for the pattern case) needed no further rewording.
No findings in this section.

## Severity and verdict
`severity_max: high` comes entirely from Finding B (accessibility). Per this role's gate rule
(`must_fix` non-empty or `severity_max >= high` → FAIL), this returns FAIL — a genuine, computed WCAG
AA failure on real reader content (both tables' column headers), not a taste call. This is scoped to
the one rendered artifact in the delta; it does not touch the settled DECISIONS.md fold, generator,
or checkers.

## Suggested remedy (not applied — read-only)
Raise `--quiet`'s light-mode value in `render-brief.py`'s `CSS` constant (and any other template
sharing the token set) until light-mode `thead th`/`.eyebrow` clears 4.5:1 — e.g. darkening toward
`--slate`'s light value (`#5b6b7c`, ≈5.34:1) closes the gap without a second token. Separately,
re-run `bin/render-brief.py` against the current markdown to refresh the stale `.html` sibling and
recover the RCE example.

---

## Amendment — lead challenge to Finding B severity

**Trigger.** The lead independently re-verified Finding B's arithmetic (undisputed) and surfaced three
facts this review did not have when it rated the finding `high`. This section records source-level
verification of those facts, the ruling, and the disposition — Finding B above is preserved unedited.

**Verified at source, not adopted from the lead's report:**

1. **Pre-existing, byte-identical, delta-independent.** `.claude/skills/harness/bin/render-brief.py:36`
   (`:root{...}` base block) and `:53` (`:root[data-theme="light"]{...}` override) both carry
   `--slate:#5b6b7c; --quiet:#7d8b99;` — byte-identical to the light-theme tokens in
   `ship-review-2026-08-29-16.html:4` / `:21` that Finding B measured. `render-brief.py:63` (`.eyebrow`),
   `:70` (`h4,h5,h6`), and `:88` (`thead th`) all consume `color:var(--quiet)` — the same selectors
   Finding B named. Independently confirmed: `git diff 2557950 48bbe7e --stat -- .claude/skills/harness/bin/render-brief.py`
   returns **no output** — the delta touches zero bytes of this file. The defect is the renderer's
   default light-mode token, unchanged by and unreachable from this delta; every briefing this
   generator has ever produced carries it, not just this one.
2. **No FEAT-38 task may touch the remedy file.** Read every `files:` block in
   `plan.yaml` (23 tasks) directly — `render-brief.py` appears in none of them. A `high` here routes
   a fix cycle whose only possible outcome is discovering the fix is out of scope; that is a wasted
   cycle, not a safeguard.
3. **Surface risk, as stated in Finding B itself:** zero interactive elements, single-operator
   internal document, dark-mode equivalent already clears AA at ≈4.86:1. Not re-verified here beyond
   what Finding B already established — carried forward as context for the ruling, not as new
   evidence.

**Ruling: re-rate Finding B from `high` to `med`.** This is not a retreat from "accessibility failures
gate" as a general rule — it is a scope call about *what this delta's review can act on*. Finding B's
computed defect is real and I stand by the arithmetic and the reach (every rendered briefing, not just
this one). What changes is the attribution: this delta did not introduce it, did not worsen it, and
holds no file that could fix it. A severity rating this review controls is meant to answer "should
*this* change be gated," and gating a change on a defect it structurally cannot touch — routing a fix
cycle to prove that — is a cycle spent, not a safeguard exercised. `med` is the right register for "a
real, confirmed, out-of-scope, pre-existing defect with a known remedy and a named owner" — it lands
on the backlog where a competent owner can act on it, without pretending this review can force a fix
through a file no task here may open.

**Named remedy owner:** a backlog row against `.claude/skills/harness/bin/render-brief.py`'s `CSS`
constant (`--quiet` light-mode value, lines 36/53) — **not** a FEAT-38 fix cycle. Whoever owns
`render-brief.py` maintenance should raise `--quiet`'s light value until `thead th`/`.eyebrow` clears
4.5:1 (e.g. toward `--slate`'s light value, ≈5.34:1), then re-run the generator against every markdown
briefing with a committed `.html` sibling to pick up the fix repo-wide in one pass — this is a shared
template, so a per-briefing patch is not the right shape of fix.

**Revised severity_max: `med`.** `must_fix` remains `[]` (unchanged from the original rating — Finding
B was never `must_fix` on its own; `high` came from `severity_max`, not from a listed blocking item).
Per this role's own gate rule, `med` does not trigger `FAIL`; this re-dispatch's verdict is `PASS`
(advisory). Finding A (`med`, unchanged, accepted) and the 18 citation hunks (accepted, no findings)
are unaffected and not reopened.
