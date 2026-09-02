# Plan-panel c5 — scope reader — FEAT-53

**BLUF.** All six fix-pass claims verified LANDED at source, independently re-derived (not taken from
pm's goal-check or the operator ruling). Structural sweep (REQ/SC tracing, `depends_on` topology,
`verify:`-vs-artifact consistency) turns up nothing new — the cycle-5 diff touched only the six named
fields plus panel dispositions, so cycle-4's clean 22/22 topology and full REQ/SC coverage still hold.
One new, non-blocking finding: `D-23`'s own explanatory text misclassifies two of its fourteen rows.

## The six claims, each graded at source

| # | Claim | Verdict | Field read |
|---|---|---|---|
| 1 | B-19/C4-01 — `T-19` git-inits the copytree, asserts clean tree + tracked `trend.jsonl`, keeps non-git failure branch | **landed** | `T-19.intent` (plan.yaml:1279-1291): `git init` + local `user.name`/`user.email` before the simulated ship; asserts `git status --porcelain` empty and `ls-files --error-unmatch` on `trend.jsonl`, explicit "present on disk is NOT the assertion"; non-git case kept, "explicitly labelled as the FAILURE-BRANCH case" |
| 2 | B-20/C4-02 — `T-10` defines UTC ISO weeks, `all` anchored at earliest record, two new fixtures | **landed** | `T-10.intent` (plan.yaml:741-753, fixtures 774-781): Monday 00:00:00Z inclusive to next Monday exclusive, bucket label = that Monday, 30d/90d first/last buckets DERIVED from `resolve_window`, `all` anchored at earliest `shipped_at`'s ISO week through `generated_at`'s week, empty series with its own reason on zero records. Both named fixtures present: "THE all ANCHOR" and "A BUCKET BOUNDARY" (two records within one minute either side of a Monday, each asserted into its own bucket) |
| 3 | B-21/C4-03 — `D-08`/`D-20`/BRIEF/DESIGN agree, alpha accepted with 3-part rollback, client build kept, zero `react-charts` in DESIGN | **landed** | `D-08.choice`/`.because` (plan.yaml:69-73): alpha ACCEPTED 2026-09-01, three-part rollback (pin+bundle; DESIGN C-2 `If absent` workaround in place; `T-18` STOP on the four hard-requirement CAPs). `D-20.because` (plan.yaml:121, full text read past the tool's 768-char truncation): "the client build is **KEPT**... server-rendered alternative was weighed and REJECTED." BRIEF `## Constraints` (BRIEF.md:73-90) carries both rulings, keeps the react-charts-is-dead sentence as history. `grep -i 'react[- ]charts'` over DESIGN.md alone: **zero** hits (the only repo hits are BRIEF.md:76's "is dead" sentence, plan.yaml:316's "NEVER @tanstack/react-charts" instruction, and two panel-note lines recording the *old, now-fixed* defect — none is DESIGN.md naming it as a live fallback) |
| 4 | B-22/D-23 — 14 accepted backlog rows named, 6 carry one-line subjects | **landed, with one caveat below** | Enumerated independently from all four `notes/answers-*.md` + `notes/ship-review-*.md` files: c1 accepted B-1..B-10 (10); c2 struck B-6, ordered B-11 FIXED (not backlog), accepted B-12..B-14 (3); c3 ordered B-15..B-18 FIXED (0 backlog); c4 ordered B-19,20,21,22,24 FIXED, accepted B-23,B-25 (2) as backlog. Total accepted-and-never-fixed = 5+4+3+2 = **14**, exactly `D-23`'s set (B-1,2,3,4,5,7,8,9,10,12,13,14,23,25). One-line subjects for B-7,8,9,10,23,25 checked word-for-word against `ship-review-2026-09-01-plan.md:126-129` and `ship-review-2026-09-02-plan-c4.md:116-118` — faithful |
| 5 | B-24/C4-06 — `12` genuinely carried by `127.0.0.1`/`122`, `3` by `3x3`/`python3`, `1024`/`ES2022` gone | **landed** | Re-computed the substrings myself: `"12" in "127.0.0.1"` and `in "122"` → True; `in "1024"`, `in "ES2022"` → False; `"3" in "3x3"` and `in "python3"` → True. `T-07.intent` (plan.yaml:578-585) and BRIEF `## Verification gaps` (BRIEF.md:157-166) cite exactly these carriers; `1024`/`ES2022` absent from both clauses |
| 6 | `panel.findings` dispositions — C4-01/02/03/04/06 `resolved`, C4-05/07 `backlog` | **landed** | plan.yaml:1918-2072: all seven read exactly as claimed, each with a `resolved_by`/citation note |

## New finding — not previously raised, not on the out-of-scope list

- **severity: low**
- **where**: `D-23.choice` (plan.yaml:163-172), contradicted by `panel.findings` ids `C4-05`
  (plan.yaml:2026) and `C4-07` (plan.yaml:2059)
- **what**: `D-23` states "B-1..B-5 and B-12..B-14 additionally carry their own panel-finding note in
  this plan's `panel.findings`; B-7..B-10, B-23 and B-25 have no panel disposition of their own."
  That is false for B-23 and B-25: `C4-05` (`disposition: backlog`, note "Briefing row B-23... carried
  by D-23") and `C4-07` (`disposition: backlog`, note "Briefing row B-25... carried by D-23") are
  themselves `panel.findings` entries with real summaries, exactly the shape B-1..B-5/B-12..B-14 have.
  Only B-7..B-10 are genuinely carrier-less (they exist solely in the immutable c1 briefing table,
  never dispositioned by any panel run).
- **consequence**: none functional — the one-line subjects `D-23` records for B-23/B-25 are
  independently correct (verified above), so a filer at ship still gets the right issue text whichever
  clause they trust. The defect is purely in `D-23`'s own reasoning about the state of the document it
  belongs to, written in the same fix pass that was specifically ordered to correct a different false
  evidence claim (B-24) elsewhere in this plan. Worth a one-clause correction (drop B-23/B-25 from the
  "have no panel disposition" list, or drop the distinction entirely since it changes no filing
  behaviour), not worth spending a cycle on alone.

## Structural sweep — nothing else moved

`git diff` region count from the goal-check (17 hunks, all six named fixes plus seven disposition
lines) checked against the task/decision graph: no task's `depends_on`, `files`, or `verify` changed
this cycle, so cycle-4's independently-confirmed 22/22 acyclic graph and full bidirectional REQ↔SC
coverage (`BRIEF.md ### Coverage`) still hold without re-derivation. Spot-checked `D-23`'s own
references (`SC-13`, `SC-15`, `T-05`) — all exist. `T-10`'s citation of "DESIGN open question Q4"
resolves (`DESIGN.md` §Open questions, Q4, present and on-topic). No orphan REQ, no task tracing to a
nonexistent REQ/SC, no `verify:` clause grepping a literal absent from its target.

## Findings summary

- `must_fix`: none
- `severity_max`: low
- One advisory finding above; ship-blocking nothing.
