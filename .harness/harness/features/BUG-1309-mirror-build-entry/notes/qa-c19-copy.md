# QA gate — c19 copy delta at 4857818b

**BLUF: PASS.** The matrix floor is met, the T-05 verify clause runs green end-to-end
(`VERIFY-PASS`, `code_grade=4`), the copy contract is still bound by an independent test after the
re-anchor, all 26 byte-frozen case names in `plan.yaml:1088` still resolve against the suite's
actual output, and the `{feat}`-drop non-reddening is a pre-existing gap, not a defect of this
delta. Test-first order cannot be established from the git record and is reported as such, not
assumed either way.

## Matrix

`change_type: feature` (`plan.yaml:1069`), matrix source `.harness/harness.json:191-202`
(`test_matrix.feature`): `always: [unit, integration]`, `when: ui if has_interaction_flow` (no
interaction flow here — a PreToolUse hook script, not skipped). `integration` is satisfied by
`tests/integration/test-merge-gate.py` (this file is directly in the diff — P-05). `unit` is
satisfied by T-05's verify's own `tests/unit/test-omp-hooks.py` step (56 pass / 0 fail, bun test).
Floor met: `matrix_ok: true`.

## Suite run

`python3 tests/integration/test-merge-gate.py`: **rc=0, ok=36, FAIL=0**, `ALL PASSED`. Matches the
c18 baseline of 36 (`notes/qa-c18.md` §1 — not re-read here, per instruction to treat prior
measurement as given). Tree clean apart from the pre-existing `feature.json` pin and sibling
reviewers' notes (not mine).

## T-05 verify, verbatim

Diffed byte-for-byte (`plan.yaml`'s parsed `tasks[T-05].verify`, 1982 bytes) against the dispatch's
quoted string: **identical**. Ran it end to end: `VERIFY-PASS` printed. `code_grade` (`g`) = **4**
(`>= 4` required, holds with no margin to spare — worth flagging as a fact, not a finding, since the
gate only needs `>=4` and got exactly that).

## a. Does the suite still bind the copy contract?

Yes. `tests/integration/test-merge-gate.py:64-66` — case `T-05 recovery-required denies` — holds
the predicate `"needs its GitHub mirror recovery completed" in reason`. **Verified by mutation**, not
inferred from suite colour: built a disposable worktree at
`.claude/worktrees/qa-mutate-1309` (bash-write-guard requires `.claude/worktrees/`, not `/tmp`;
recorded as gotcha below) pinned at 4857818b, replaced the `deny(f"...")` call at
`merge-gate.py:192` with a neutral string. Result: **3 cases redden** —
`T-05 recovery-required denies`, `T-05 non-era absent build_entry denies naming feature and
re-run command`, `T-05 unresolvable gh falls back and denies a locally owed receipt`. Restored via
`git checkout --`; `git status --porcelain` confirmed clean before worktree removal.

## b. Test-first compliance

**Cannot be established from the record; reporting as such.** Both the source hunk
(`merge-gate.py:192`) and both test hunks (`test-merge-gate.py:64-65`, `:99-102`) are in the single
commit 4857818b — `git show --stat` shows exactly 2 files changed, no intermediate commit, and
`git reflog` shows one commit event for this hash with no earlier staged/amended state. There is no
separate "red" commit, no CI run record, and no note in
`notes/rulings-2026-09-08-c19-copy.md` asserting the actual chronological order the edits were
made in (it states the required *outcome* — "must redden each time" — not the order of authorship).
A single atomic commit combining a copy change with its two dependent test-predicate updates is
consistent with either order (test-first-then-committed-together, or edited-together); the record
does not discriminate between them. This is not itself a defect — atomic copy+test commits are
normal for a re-anchor — but the specific claim "the updated expectation failed before the source
edit landed" is not one this record can confirm or deny.

## c. All 26 byte-frozen case names

**All 26 matched**, verified individually (not via a file-global grep) against the actual suite
output lines. 25 are exact matches. One is the documented prefix case:
`plan.yaml:1088` lists `"T-05 non-era absent build_entry denies"`; the suite's real case name is
`"T-05 non-era absent build_entry denies naming feature and re-run command"`
(`test-merge-gate.py:68`). Since `grep -qF "ok    $n"` is an unanchored substring match, the listed
name is a strict prefix of the real name and the check holds. No other of the 26 listed names is in
this relationship — every other listed string is byte-identical to its printed `ok` line.

## d. Did any assertion get weaker?

Read `merge-gate.py:190-192`: `command_line` is built from `command_name` (`"open"` for this
fixture, via `feature_schema.recovery_command_for`, confirmed at `feature_schema.py:324-327`) and
`os.path.realpath(feat_dir)` (which embeds the directory name `FEAT-9001-fixture-non-era`). **Both**
new-predicate tokens — `"FEAT-9001-fixture-non-era"` and `"gh-sync.py open"` — live entirely inside
`command_line`, sourced from two different constructor inputs (the realpath'd directory vs. the
resolved command name), so the conjunction is two independent facts about one rendered field, not
one fact asserted twice.

(i) Not weaker for what this case exists to prove — "an unresolvable `gh` falls back and still
denies a locally owed receipt." The new predicate confirms the reason names the specific feature
*and* the concrete, actionable recovery command; the old `"absent" in reason"` only confirmed the
literal fallback-value token appeared, saying nothing about which feature or what to run.

(ii) The old `"absent" in reason` bound one thing nothing now binds on this path: that the raw
recorded value (`value = entry or "absent"`, `merge-gate.py:186`) is surfaced in the message. On
the repo-pinned deny path (`:192`), `value` is computed but never referenced in the emitted string —
only the unpinned-repo branch (`:188`) still surfaces it. This loss is **intended**, per D-19
(`plan.yaml:330-342`): the ruling names `github.build_entry=<value>` as deliberately-removed jargon
the operator could not act on. Not an unintended gap.

## {feat}-probe grade

Verified independently: dropping `{feat}` from the f-string (leaving `command_line` intact) reddens
**zero** cases (0 FAIL across the full 36-case run). This is **(ii) a pre-existing test-strength
gap, belonging on the backlog, not (i) a defect in this delta**: the case carrying the affected
predicate (`T-05 non-era absent build_entry denies naming feature and re-run command`) is unchanged
by 4857818b except for the substring literal it matches against — its structural blindness to
`{feat}` specifically (because `command_line`'s embedded directory path already satisfies the
feature-name check) predates this commit and this commit did not introduce or worsen it.

## Findings

- **F-01** (info): `code_grade=4` meets the `>=4` floor with zero margin — not a failure, but the
  gate has no slack; a future refactor of `git_merge`/`words`/`direct_merge`/`gh_merge` that adds
  even one branch could flip this gate red without touching behavior. (`merge-gate.py:192` region)
- **F-02** (info/backlog): the `{feat}`-drop blindness in
  `T-05 non-era absent build_entry denies naming feature and re-run command` (`test-merge-gate.py:67-69`)
  is a pre-existing test-strength gap: it cannot discriminate loss of the literal `{feat}` token
  because `command_line`'s embedded realpath already carries the feature name. Not blocking this
  cycle; worth a future task if `{feat}`'s own presence in the sentence (independent of the path)
  ever needs its own proof.

No `high`/`critical`/`med` findings. Both items above are informational/backlog per the grading
instructions (§5): reasoned from predicate text and mutation, not suite colour.
