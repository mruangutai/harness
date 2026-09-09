# Observations - harness-pm

- 2026-09-08: BUG-1507 - the issue enumerated four surfaces; a fifth live occurrence of the same defect sat one line group above the first (board-station.py <issue-number> Plan at harness-plan.md:11, measured exit 2). Sweeping the whole instruction scope with the tool's own accepted-station set found it; grepping only the cited anchors would not have.
- 2026-09-08: BUG-1507 - a line-wrapped command in markdown (github-mirror.md:55-56, tool name ending one line and station argument beginning the next) is invisible to any line-anchored grep. Collapsing whitespace before matching is what made the occurrence FEAT-41's migration missed visible; every task verify block uses the collapsed form for that reason.
- 2026-09-08: BUG-1507 - proving each task verify twice paid: on the unbuilt tree (all five non-zero, each for its own reason) and again on a scratch copy carrying the intended fix (T-01..T-04 all zero). Only the second run proves a verify can turn green rather than being permanently red.
- 2026-09-08: BUG-1507 - harness.json test_matrix maps bugfix plus fix_confined_to_tests_and_contract_docs to integration, which turns "should we add a witness?" into a matrix obligation for any doc-confined bugfix. Typing the machine-checkable prose fixes bugfix and the wording-only ones docs is the honest split; typing all of them docs would dodge the gate.
- 2026-09-08: BUG-1507 - a plain YAML scalar carrying "board-station: 'Plan' is not a station" broke plan-merge apply with a mapping-values error, exit 5. Colon-space inside a plain scalar again; rewrote with dashes rather than quoting.
- 2026-09-08: BUG-1507 goal-check — an SC graded on a command's exit status is not graded on its
  effect: gh-sync.py:1353-1356 exits 0 printing "no sub-issues recorded, nothing to move", and the
  feature's feature.json had no github key at all, so SC-01 could read met with zero cards moved.
  Grade the observable the operator named, not the command's status.
- 2026-09-08: BUG-1507 goal-check — a DoD bullet with no REQ, no SC and no constraint line is
  invisible to every downstream gate; bullet 2's exclusivity claim was also half-false on disk
  (gh_board.py:192-202 reads an absent task status as ready). Enumerate the DoD bullets against the
  BRIEF explicitly; internal consistency of a plan says nothing about coverage.
- 2026-09-08: BUG-1507 goal-check — post-signature SCs graded on "this feature's own run" fail for a
  reason unrelated to the fix when the actor loads the instruction from the control-plane checkout
  while the fix lives only in the worktree. Name which copy the actor follows.
- 2026-09-08: BUG-1507 plan-fix c1 — the fix-cycle dispatch mandated `plan-merge.py apply` for
  changing an existing task value; apply exits 7 CONFLICT on any changed value (plan-merge.py:738),
  so both intent repairs went through `amend --expect-sha256 --value-file`. Raised as a non-blocking
  open question rather than worked around silently.
- 2026-09-08: BUG-1507 — a decoration sweep over plan.yaml values flags `**` from the glob
  `.claude/skills/**/*.md` (D-05 choice, T-05 intent). Legitimate; the no-markdown rule is about
  bold/backticks/links, so a glob hit is not a violation to "fix".
- 2026-09-08: BUG-1507 panel record. plan-merge set-panel splices `panel:` BEFORE `tasks:`, so every
  task line number in the plan shifts by the panel's height. Findings whose summaries cite
  `plan.yaml:<line>` therefore point at pre-panel positions the moment they are recorded, and the
  summary must NOT be corrected because rewording remints the PF- id.
- 2026-09-08: proving a strengthened final conjunct of an and-chain needs a fixture where the earlier
  conjuncts are green; on the unfixed tree T-02's `all(islower)` short-circuits first, so the new
  conjunct never ran and its discrimination would have been assumed. Staging the FIXED file plus a
  wrong-tool variant is what measured it.
- 2026-09-08: a verify slicing a markdown region can carry `**` in its delimiter literals, which the
  no-markdown-in-values rule then flags. Bare-text delimiters (`The eng segment.`) were unique in the
  block here, so uniqueness-counting both candidates first avoided the trade-off entirely.
- 2026-09-08: BUG-1507 T-03 verify amend. A `verify:` that slices correctly can still fail open on the SEARCH TERM: the bare phrase `set-feature-station --station building` passed on a fixture where the tool name was absent and where a wrong tool (`gh-sync.py`) wrote it. Proving a term binds needs four fixtures, not one: full, wrapped, term-absent, wrong-subject — plus the old command on the term-absent fixture to show the residual was real (it exited 0).
- 2026-09-08: A contiguous-literal search over a doc region is only safe when the region is whitespace-collapsed first; SKILL.md wraps commands across lines. Also checked the target file's own style (segment 4, SKILL.md:156) puts the whole invocation in one backtick span — that is what makes the literal survive a style-matching edit, so "is the literal brittle here?" is answered by reading the neighbouring convention, not by guessing.
- 2026-09-08: `plan-merge.py amend --show` prints the field body plus its sha256, so the expect-sha256 round trip needs no separate hashing. Panel-key immutability is cheapest to prove with a canonical-JSON sha of the whole `panel` key taken BEFORE the amend, then re-taken after, alongside re-hashing each summary with panel_findings.py id.
