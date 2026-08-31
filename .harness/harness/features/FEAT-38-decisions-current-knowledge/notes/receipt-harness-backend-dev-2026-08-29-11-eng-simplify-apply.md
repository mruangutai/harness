# Receipt — harness-backend-dev — SIMPLIFY/apply — FEAT-38

Task: apply exactly three eng-lead-adjudicated edits from the SIMPLIFY pass, re-run suites.
No PLAN task id (`task: none`) — a between-gate apply, not a plan task.

## Edit 1 — `.claude/skills/harness/bin/test-no-distribution.py:71-73`

Sub-verifications, expressions used:
- (a) DEC-162 live, not about map tier: `grep 'DEC-162' DECISIONS-INDEX.md` → row
  `DEC-162 @3774 [map,domain,approval,state] ... :: Mission map assigns pm
  .harness/codebase/glossary.md ... check-state INV-19 warns when a mapped codebase
  carries no glossary.` — no STRUCK marker; read full body `DECISIONS.md:3774-3793`,
  confirms it's the glossary-enforcement ruling, unrelated to map-tier retirement.
- (b) DEC-149 live and its body states the map-tier retirement: read `DECISIONS.md:3306-3337`
  (heading `## DEC-149`, no STRUCK marker). Body lines 3329-3331: "A third import, the
  `deepen` mission, was tried and retired... the map tier was removed after 35 features
  never built one — leaving the mission nothing to scan." Confirms the retirement fact lives
  here.
- (c) original DEC-137 is struck: `grep -n '## DEC-137' DECISIONS.md` → no match (fully
  removed, consistent with a struck-and-purged entry); `git log --all -S"DEC-137" --oneline
  -- .harness/harness/docs/DECISIONS.md` → top hit `ac61b44 Retire the codebase map tier:
  DEC-137 and DEC-140 struck (#815)`. Confirmed struck.

All three verified. Rewrote the sentence (not a digit swap) to cite DEC-149 and drop the
untrue "struck" clause:

Before:
```
    # Four doors, not six: /harness-map and /harness-deepen were deleted when the
    # codebase map tier was retired (DEC-162, struck 2026-08-24). The guard is that a
    # distribution sweep does not take the REMAINING doors with it.
```
After:
```
    # Four doors, not six: /harness-map and /harness-deepen were deleted when the
    # codebase map tier was retired (DEC-149 records the removal). The guard is that a
    # distribution sweep does not take the REMAINING doors with it.
```

## Edit 2 — `gen-decisions-index.py:94` (`defenced_lines` docstring)

Confirmed no `compute_amendments` / amendment extraction remains in the file
(`grep -n 'compute_amendments|amendment'` → only the docstring's own now-stale mention).
Dropped `amendments, ` from the consumer list; ordering-guarantee meaning unchanged.

Before: `harvested. This must run BEFORE all extraction: headings, amendments,\n    the reference graph, and tag scoring all see the de-fenced body.`
After: `harvested. This must run BEFORE all extraction: headings,\n    the reference graph, and tag scoring all see the de-fenced body.`

## Edit 3 — `gen-decisions-index.py:172` (inside `build_index`)

Confirmed (i) `parse_decisions` has exactly one caller, `build_index` line 172
(`grep -n 'parse_decisions('` → definition line 109 + one call site line 172).
Confirmed (ii) `lines` unread anywhere later in `build_index` (full body read
lines 171-216: only `decisions` and `headings` used downstream). Applied the
single-token rename, no signature/return-shape change.

Before: `    decisions, lines, headings = parse_decisions(text)`
After: `    decisions, _, headings = parse_decisions(text)`

## Post-apply gates (all measured in the worktree)

- `check-decision-anchors.py`: exit 0, "examined 20 anchor(s), 0 failed"
- `check-decision-claims.py`: exit 0, "examined 11 claim(s), 0 failed"
- `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md`: exit 0, empty diff
- `run-unit-tests.sh` (output captured to a shell variable, never piped to head/tail):
  runner exit `$?` captured immediately = 0; `grep -c '^FAIL'` = 0;
  `grep -c 'PASS'` = 1150; `grep -c '^KIND-DRIFT:'` = 0.
  No repair attempt needed — suite was green on first run after the edits.

## Diff-stat proof (working-tree form, no revision range)

`git -C <worktree> diff --stat -- .harness/harness/docs/DECISIONS.md
.harness/harness/docs/DECISIONS-INDEX.md` → empty output, exit 0. Neither frozen doc file
touched.

## Status proof

`git -C <worktree> status --porcelain` lists exactly: the two edited scripts, this receipt,
and prior-run sibling artifacts (qa validator note, four eng-simplify-angle receipts, a
grilling note) — nothing under `.harness/harness/docs/`.
`git -C /Users/molchairuangutai/GitHub/harness status --porcelain` shows only pre-existing
untracked main-checkout artifacts from unrelated features — nothing from this apply.

HEAD unmoved: `git -C <worktree> rev-parse HEAD` = `384b80048cedda7fc9b9843c6fc7a82249c22467`.
