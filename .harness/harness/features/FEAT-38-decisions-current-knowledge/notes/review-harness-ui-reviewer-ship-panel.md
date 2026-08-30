# UI review — FEAT-38 ship panel (pin `635cd3b`)

**Conclusion: no UI surface for this role to review in this diff. Measured, not predicted.**

## 1. Measured census (Python, `git diff --numstat 7ebfc9eb…635cd3b`)

- **137 files changed** total.
- Extension breakdown (by basename suffix, counted in Python — `/usr/bin/grep` on this
  machine is a non-GNU `pi-uu-grep 0.2.0` and was not used for any count in this report):

  | ext | count |
  |---|---|
  | md | 104 |
  | py | 21 |
  | sh | 3 |
  | yaml | 2 |
  | json | 2 |
  | html | 2 |
  | snippet | 1 |
  | yml | 1 |
  | gitignore | 1 |

  Total 137, matches the file count. No css/scss/tsx/jsx/vue/svelte/less anywhere in the diff.

## 2. `DESIGN.md` existence check

`git ls-tree -r --name-only 635cd3b .harness/harness/features/FEAT-38-decisions-current-knowledge/`
returns **91 files, zero of which have `DESIGN` in the name.** No design contract exists for this
feature at the pin. A contract that does not exist cannot be violated — measured fact, not inference.

## 3. The two `.html` hits — investigated, ruled out of scope

The census surfaced two genuine HTML files, both wholly new (0 deletions each):
`notes/ship-review-2026-08-29-16.html` (112 lines) and `notes/ship-review-2026-08-29-18.html`
(120 lines). Read at the pin: these are fully-styled documents with CSS custom-property theming,
a `prefers-color-scheme` dark-mode media query, and an explicit `data-theme` override — i.e., they
look exactly like the kind of surface this role exists to audit.

They are not this feature's deliverable, though. `.claude/skills/harness/bin/render-brief.py`
carries the docstring "Render a ship-review briefing into a reading view — DERIVED, NEVER
AUTHORED," and `SKILL.md:286-289` confirms the convention: the markdown is the record, the sibling
`.html` is a mechanical rendering, "never hand-authored" (DEC-141). I confirmed `render-brief.py`
itself is **byte-identical between base and pin** (`git diff --stat 7ebfc9eb…635cd3b -- …render-brief.py`
returns empty) — this feature did not touch the generator. The two HTML files are process receipts:
snapshots of running the harness's own ship-review pipeline against FEAT-38, committed for the
historical record the same way the ~40 `receipt-*.md`/`research-*.md` files in this diff are — no
reviewer role judges those, and this generator's template is pre-existing, unmodified tooling, not
a surface this feature designed or built. Out of scope.

## 4. `DECISIONS.md` / `DECISIONS-INDEX.md` — human-read, explicitly judged out of scope

Both are plain markdown, read via editor/`git show`/GitHub's default renderer — no template, no
CSS, no `DESIGN.md` binds either of them.

- `DECISIONS-INDEX.md` is a fixed single-line row grammar
  (`- DEC-NN @<line> [tags] refs: <graph> :: <ruling>`), not a table — 3 stray `|` characters in
  the whole 205-line file, none forming a `|...|` row. There is no "table structure" to audit here.
- `DECISIONS.md` does contain 171 lines matching GFM table-row syntax (`Claim | Reality`-style
  comparison tables). I checked whether this diff introduced that convention: the pre-feature
  baseline (`git show 99bb52c:…DECISIONS.md`) has the **identical count, 171**. The convention
  predates FEAT-38 and is unstyled default GFM — this feature edited table *content* (part of the
  605/1747 line delta) but did not introduce or restyle a table surface.

Judgment: these are content/documentation artifacts (the documentor's and code-reviewer's remit —
does the prose say what's true, does the generator emit correct rows), not a visual design contract
with spacing/colour/state/accessibility properties this role has any basis to check. I looked at
both before ruling this, per the task's explicit invitation to review table structure "if in scope."

## 5. Other small edits scanned for user-facing text

`check-domain.sh` (comment-only, strips a stale `am.1` amendment reference), `run-unit-tests.sh`
(one array entry added), `.harness/harness.json` (one glob entry added) — none touch a message a
human reads as rendered/terminal output. Looked, nothing to report.

## Verdict rationale

Every changed-file class in the panel's shared surface list was checked at the object level, not
assumed: no CSS/JS/component files exist in the diff; the only two rendered files are derived
receipts from unmodified tooling; the two authority markdown docs carry no design contract and no
new table/rendering convention. `in_scope: false` is the correct, measured outcome.
