# Plan-panel review — scope reader — BUG-148-gate-record-correction

**BLUF: no gating defect. The load-bearing factual claim is CONFIRMED at source. Two med findings
worth a signature-time look; nothing blocks. Read-only throughout — no file touched but this note.**

## The load-bearing claim (item 2): CONFIRMED

D-01/D-02's claim — that on 2026-08-03 `gen-decisions-index.py --check` fell through to the WRITE
path because argv validation did not exist until `ffbdbfa1` (2026-08-05), so the exit 0 was a
regeneration and could not prove drift — is **CONFIRMED**, not merely plausible:

- `git show 99b380e3:.claude/skills/harness/bin/gen-decisions-index.py` (the version in effect
  2026-08-02 through 2026-08-04, i.e. covering 2026-08-03 — verified no intervening commit touched
  the file: `git log --oneline 99b380e3..ffbdbfa1 -- '*/gen-decisions-index.py'` returns only
  `ffbdbfa1` itself) shows `main()`: `stdout_mode = "--stdout" in sys.argv[1:]` (line 371), no argv
  validation anywhere, and at the end of the function `if stdout_mode: ...; return` else falls
  through to `with open(INDEX_PATH, "w", ...) as f: f.write(output)` with no further `sys.exit`
  (line ~410-415). `--check` never matches `"--stdout"`, so `stdout_mode` is `False` and the
  function falls to the write branch and returns normally → **process exit 0, index rewritten.**
- `git show ffbdbfa1` (the fix commit) states the same mechanism in its own commit message,
  independently: *"the script had no argument validation at all, so `sys.argv` was consulted for
  exactly one string — `--stdout` — and EVERY other token... fell through to the default branch,
  which WRITES... in place."* It also names DEC-174's evidence paragraph directly as one of the six
  sites carrying the stale claim.
- `.harness/harness/docs/DECISIONS.md:4308-4309` at `41c16c7` reads exactly as the BRIEF states:
  "Every gate was green — ...`gen-decisions-index.py --check`— while:" — confirming the record under
  correction says what the plan says it says.

No critical finding on this axis. Both corrections rest on a true premise.

## Verify blocks: discriminate correctly, one mechanical gap (item 3)

Executed both `verify:` blocks as static reads against `41c16c7` (not modified, read-only `git show`
+ shell string ops):

- **T-01**: `sed -n '/^## DEC-174 /,/^## DEC-175 /p'` correctly isolates the DEC-174 body (headings
  measured at `DECISIONS.md:4302` / `:4424`). Pre-correction: `'Every gate was green'` **is present**
  → the first branch fires, verify **fails** (`exit 1`), as required. All five required phrases are
  **absent** pre-correction except `2026-08-03`, which is already present via the untouched bold
  lead-in ("all from 2026-08-03") — harmless, since T-01's intent explicitly preserves that
  lead-in, but it means that one grep is non-discriminating on its own (satisfied by unrelated
  preserved text, not by the corrected sentence).
- **T-02**: pre-correction STATE.md measured at 165 lines, 7 `## ` headings (matches D-04). Stale
  phrase `'All four gates green'` present, all five correction phrases absent → verify **fails**
  pre-correction as required. Heading-count assertion (`= 7`) is a stable invariant, not a race.

**The gap**: both verifies are five independent `grep -F` substring checks plus one narrow negative
check (`'Every gate was green'` / `'All four gates green'` — one exact phrase each). Neither checks
that the retained text `gen-decisions-index.py --check 0` (or `--check` named as a gate that
"exited 0") is *itself* absent or clearly subordinated — only that one specific summary sentence is
gone. A technically-compliant-but-lazy execution could satisfy every grep by stapling the five
required phrases onto the tail of a sentence that still separately asserts `` `gen-decisions-index.py
--check` 0 `` as a bare fact, and the mechanical verify would pass while the record still reads as
misleading. The BRIEF's own "Verification gaps" section discloses this ("the wording of a decision
record cannot be graded by any runner") and defers entirely to SC-06 (uat, the operator's own read)
— so it is a known, accepted gap, not an oversight, but it means SC-06 is the *only* check standing
between a grep-satisfying record and a misleading one. **severity: med** (mitigated by design via
SC-06, not a runtime defect, but worth the panel's attention since no earlier checkpoint catches it).

## Intent-vs-form divergence, D-01 (item 1): confirms and sharpens the prior goal-check's F-2

Read at source: **DEC-205**'s own heading is "**This file** states current truth" — it is scoped to
`DECISIONS.md` (`docs/DECISIONS.md:6320`) and says nothing about `STATE.md`. D-01's "because" clause
correctly attributes the DECISIONS.md prohibition on an appended note to DEC-205, but for STATE.md it
gives a *different* reason: "barred from a new section by its two-heading vocabulary." Read
`check-domain.sh:1796-1805` directly: the STATE.md shape gate rejects only `## ` **headings** outside
`## Current`/`## Open Questions` (`bad = [h for h in h2 if h not in (...)]`) — it says nothing about
body content *within* an existing heading. An inline dated sentence appended inside `## Current` (no
new `## ` line) would not trip this gate at all. So the "two-heading vocabulary" genuinely forecloses
a **new section**, but does not foreclose an **appended note inline** — which is closer to what the
operator settled on (grilling: "add a dated note"). D-01 presents the in-place-rewrite-not-append
choice as equally forced for both records; for STATE.md it is a preference, not a constraint. (T-02's
actual delivered text is, in substance, close to a dated inline note — it names 2026-09-06 and the
correction language in place of the false line — so the practical gap is narrower than D-01's stated
reasoning suggests, but the reasoning itself overclaims.) The prior goal-check flagged this
substantively as F-2 and recommended a one-line confirmation at signature; I concur with that
diagnosis, sharpened by the direct `check-domain.sh` read above, and note the plan as drafted contains
no such confirmation step — SC-06 asks whether the correction "reads as current truth," which is a
related but not identical question to "do you accept rewrite-in-place over the appended note you
asked for." **severity: med.**

## Lane and shape (item 4): confirmed honest, no defect

`bash .agents/skills/harness/bin/check-domain.sh --resolve
.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md` → `harness-orchestrator`, exactly
matching D-02's claim. `check-domain.sh`'s own comment (`:255-257`) confirms `harness-orchestrator` is
a bare top-level key carrying its own `domain:` grant, governed like any other agent since DEC-120 —
this is not a special carve-out, the lane is honest. D-04 (Edit not Write, pre-existing violation left
as found) is confirmed correct: the shape gate's route-refusal logic denies `Write` pre-hoc (whole-file
`content`) but exits 0 pre-hoc for `Edit` (no `content` in the payload), reporting shape violations
only post-hoc via `deny()` inside `shape_problems()`. Leaving a completed feature's pre-existing
165-line/7-heading violation untouched, rather than doing an out-of-scope shrink mid-correction, is a
reasonable scope call — no defect.

## SC-01/SC-02 redundancy (item 5): confirms prior goal-check F-4, not re-raised as new

SC-01 and SC-02 (BRIEF) are, verbatim, the same phrase-presence/absence checks as T-01's and T-02's own
`verify:` blocks, read via `git show <review_sha>:path` instead of the live worktree file. They add no
independent measurement — of the six SCs, only SC-03 (diff-scope), SC-04 (regression suite, confirmed
already green pre-correction), SC-05 (file-scope, now re-baselined on `41c16c7`), and SC-06 (uat) are
independent. This is the same conclusion the prior goal-check reached (F-4, low) — re-derived here,
not re-raised as a new item.

## No orphans, no topology issue

REQ-01..05 all traced (T-01: all five; T-02: REQ-01..04, correctly omitting REQ-05 which is T-01's
index-sync-only responsibility). `depends_on: []` on both tasks is correct — disjoint files, no
ordering needed. No task serves a REQ that doesn't exist; no REQ or SC is owned by nothing (SC-06 is
uat, legitimately owned by the operator's read rather than a task).

## Findings summary

| # | Summary | Severity | Concrete consequence |
|---|---|---|---|
| 1 | Grep-based verify checks one exact stale phrase, not the broader false claim; a stapled-on correction could satisfy every grep while still separately asserting `--check` exited 0 as fact | med | SC-06 (a single human read at signature) is the only backstop; no earlier checkpoint catches a keyword-stuffed non-correction |
| 2 | D-01's "because" clause for STATE.md overclaims: the two-heading vocabulary bars a new section, not an inline appended note, so rewrite-vs-append was a preference dressed as forced (concurs with, sharpens, prior goal-check F-2) | med | Plan as drafted has no confirmation step surfacing this to the operator before signature; SC-06 asks a related but not identical question |
| 3 | SC-01/SC-02 duplicate T-01/T-02's own verifies; only SC-03/04/05/06 independently measure (concurs with prior goal-check F-4, not re-raised as new) | low | Six SCs read as six checks; substantively four |

No must_fix. No critical/high finding. The load-bearing factual premise (item 2 of the batch context)
is CONFIRMED, which is itself the most consequential result of this review — had it been wrong, both
corrections would have installed a new falsehood, and that was not the case.

**No file outside this note was created or modified.** All verification was `git show`, `sed -n`,
`grep`, and in-memory shell string comparisons against commit `41c16c7` and historical commits
(`99b380e3`, `ffbdbfa1`); no working-tree file was written, and no `git checkout`/HEAD move occurred.
