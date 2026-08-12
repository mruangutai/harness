# Observations — harness-pm — FEAT-16-factory-per-repo-board

- 2026-08-11: a `verify:` command I wrote from memory did not exist. T-10 shipped
  `gen-decisions-index.py --check` through a full plan cycle and an architecture review; the tool
  answers `unrecognized argument(s): --check`, exits 2, and prints the real form
  (`--stdout | diff - docs/harness/DECISIONS-INDEX.md`). Nothing in check-plan-routes.py or
  check-state.sh executes a `verify:` string, so a non-existent flag is invisible until the doer
  runs it. Running each new verify block before shipping the plan is what caught it.
- 2026-08-11: a multi-clause `verify:` block separated by newlines reports only the LAST clause's
  status if the runner executes it as one shell invocation without `set -e`. On T-07 that would
  have made the two board clauses decorative and left only the MF-3 regression guard live. Chained
  with `&&` and checked with `bash -n` through `yaml.safe_load` (not by eye — the literal block's
  content is what runs).
- 2026-08-11: `test "$(grep -c PHRASE file)" -ge 2` passes when one row carries the phrase twice.
  The review asked for a phrase in two specific index rows; the count form cannot see the
  distribution. Replaced with one `grep -E "^- DEC-NNN " file | grep -q PHRASE` per row.
- 2026-08-11: `lanes.resolved_at` was `d97f5ea`, which `git merge-base --is-ancestor` says is NOT an
  ancestor of HEAD (`a29ad06`) — it exists in the object store but is off this line. `git diff`
  between the two over `check-domain.sh` and `check-state.sh` is empty, so the decision resting on
  those files survived, but the sha would not have resolved for a later reader on this branch.
  SC-03's board measurement is still labelled `d97f5ea` by operator instruction: that one is a
  timestamp for a live `gh` measurement, not a code anchor.
- 2026-08-11: the tree-wide `check-plan-routes.py` plan count moved 11 → 12 between two runs inside
  one session — another agent landed a plan concurrently. A recorded count from a shared tree is a
  measurement of a moving object; the per-plan violation count is the stable figure.
- 2026-08-11: DECISIONS.md amendments APPEND and supersede; they never edit the falsified sentence
  (DEC-174 am.1, DEC-179 am.2 both leave the original standing). A review item asking for an
  absence-grep over an amended entry is therefore unsatisfiable by construction — the provable
  claims are the amendment's own text and the index row, which IS rewritten in place.
- 2026-08-11 (re-baseline): the dispatch asserted "`check-plan-routes.py` contains no budget logic at
  all" and told me to verify it. FALSE — `MACHINE_LINES_PER_TASK = 50` with a `VIOLATION` branch
  naming DEC-182. The real reason the note's FEAT-14 claim did not reproduce is narrower and
  stronger: `BUDGETED_FIELDS` EXCLUDES `intent:`, so intent length cannot ever produce a budget
  violation, and FEAT-14's machine-field maximum is 46 against a cap of 50. "The mechanism cannot
  fire on what was measured" is falsification-proof where "the figures don't reproduce" is not.
- 2026-08-11 (re-baseline): a falsified-vocabulary sweep must run over `plan.yaml` as well as
  `BRIEF.md`, and the dispatch's line ranges named only the BRIEF. `grep -n` for the dead tokens
  found the same dead argument living in `plan.yaml`'s D-02, D-04 and D-07 `because:` fields and in
  T-10's intent — a criterion re-based on top of falsified reasoning one file over is the same
  defect in a new place.
- 2026-08-11 (re-baseline): a plain multi-line YAML scalar breaks on `word: word`. Three of my new
  `because:` fields did (`not two:`, `not made:`, `exactly:`), each caught only by the loader, each a
  one-character fix to an em-dash. Run the gate after every batch of decision-prose edits, not once
  at the end — the parse error names one line and hides the rest.
- 2026-08-11 (re-baseline): two boards can share option NAMES while three of six ids differ and three
  match, because GitHub reuses default template ids (`Backlog f75ad846`, `Building 47fc9ee4`,
  `Done 98236657` are identical on projects 2 and 3). So a cross-board id assertion is vacuous while
  looking more precise than the name check that actually discriminates.
