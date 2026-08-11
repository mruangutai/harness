# Fix cycle 2 — MF-9: the corpus is resolved by glob at build time

**All six parts closed. Both files edited; no `files:` block touched, so no evidence line was
traded away.** T-04 stays at 50/50 machine-field lines and T-08 at 49/50 — the equal-line-count
branch succeeded, so the thirteen-line glob trade on `files:` was never needed.

## The corpus mutated a third time, and it is worse than reported

Measured at HEAD `f3452bf` (branch `chore/203-end-copy-distribution`; the operator's `96d5d5c` is
two commits back on this same branch). `git diff --stat 96d5d5c..HEAD -- .harness/features/` shows
**four files, all `notes/` additions under FEAT-12, 806 insertions, zero deletions** — no
`feature.yaml`, `plan.yaml` or `BRIEF.md` differs between the operator's SHA and mine.

- `check-state.sh` now reports **seven** VIOLATION lines, not four. Only FEAT-14's unapproved BRIEF
  survives from the `06ae963` reading. FEAT-12's missing `handoff-plan.md` has cleared; FEAT-15 has
  gained four `STATE.md`-references-absent-task violations plus an unapproved BRIEF; the
  runs/-without-a-feature-file violation has moved from FEAT-15 to FEAT-13.
- `check-plan-routes.py` now examines **9 plans, not 10** — FEAT-13's `plan.yaml` went with the rest
  of its directory contents. **0 violations** holds.

The operator's own baseline figure rotted inside the session that produced it. That is now written
into the BRIEF as the justification for the build-waits ruling.

## What changed

**Operating set (a).** T-04 and T-08 intent now carry an explicit `THE OPERATING FILE SET IS A GLOB`
paragraph: enumerate `.harness/features/*/feature.yaml` at run time, sort, migrate exactly that. The
`files:` block is labelled in both as a plan-time routing declaration and an illustrative snapshot,
explicitly stale, explicitly not the list to iterate. **The literal list was deliberately NOT
re-enumerated to today's corpus** — that would re-enact the defect and be wrong again by build time.

**No count assertions (b).** `len(rec) != 14` became a per-directory set difference (P-04: a set
assertion, not a count match, so a stray receipt cannot cancel a missing one). `< 14 feature.json`
became `< len(drop receipts)`, directional so a corpus that grew between T-04 and T-08 does not fail
spuriously. Titles, SC-06, SC-10, and every intent count-claim are either count-free or anchored to
a named SHA/date as stated history.

**Captured baseline (c).** T-08's frozen `B` list is gone. T-04 captures the live VIOLATION set to
`notes/baseline-check-state.txt` **before its first write** — not immediately before conversion, as
the dispatch suggested, because by T-06 the gate reads `feature.json` while the corpus is still
YAML, so a capture taken then is a degenerate all-INV-18 window that makes non-growth vacuous.
Capture is never overwritten on resume (mirrors T-04's receipt hazard). Comparison keys on the text
before the em dash with `feature.yaml`→`feature.json` normalisation, because T-06 changes both the
filename *and* INV-18's remediation sentence. A missing capture raises and fails the task, by
design — and **T-04's own verify now fails if the capture file is absent**, so the omission cannot
be discovered at T-08 after the pre-migration state is gone. Timing is pinned in T-04's intent as
step 0 taken *after* the precondition is re-confirmed, in the same sitting as the rewrites; a
capture taken at task start and held through a wait for FEAT-12 would be stale by the same
mechanism. The em dash in both keying expressions is written as the escape `\u2014`, so the
`verify:` string transported verbatim to the member is pure ASCII and cannot be normalised in
transit into a mismatch. Growth-by-count is now checked as well as novelty-by-text. `P` pinned-count
logic untouched.

**runs/-without-a-feature-file (d).** Both tasks: not in the glob, therefore **skipped**, named in
the task's report as `skipped-no-feature-file`, no feature file created for it.

**Precondition (e).** The three-flow confirmation and the starts-during-the-window clause stand
verbatim. Keeping the three named is still right — they are the flows whose *signature* is the
hazard, which is a different question from which files exist, and "every live flow at build time" is
what the re-confirmation clause already requires. FEAT-15's stale "no execution-state file" reading
is now marked as a `06ae963` reading with its 2026-08-10 correction beside it.

**FEAT-15 corroboration (f).** Written as corroboration of the **twelve-key** schema with `github`
and `factory` legitimately omitted — verified directly: FEAT-15's `feature.yaml` loads to exactly
`[feature_id, branch, pr, status, phase, review_sha, cycles_used, max_total_cycles, max_total_runs,
runs]`, `pr` is the string `none`. Not a ten-key floor.

## Also fixed, and invisible to a `14` grep

Both tasks asserted **"FEAT-15 is outside this migration; do not create one for it"** — false at
HEAD. After the glob change the build agent would have been handed FEAT-15 by the glob and told not
to convert it, producing a skipped file that then trips T-08's `if y:` no-YAML-remains check. Same
for `BRIEF.md`'s "FEAT-15 has none, so it is outside the migration set". All removed.

T-04's resume prose ("the verify clause asserts exactly 14 receipts") contradicted the clause it
describes and was rewritten with it (P-08).

## Verified

- Both `verify:` bodies `compile()` clean.
- T-04's receipt set-difference and T-08's em-dash keying were executed against live
  `check-state.sh` output: 7 baseline keys, zero false novelty on self-comparison.
- Read-only on FEAT-13 and FEAT-15 throughout; nothing written under either.

## Open

Nothing blocking. No approved decision or goal was changed — `approval.status` is `pending` in both
`plan.yaml` and `BRIEF.md`, so the edits are pre-signature.
